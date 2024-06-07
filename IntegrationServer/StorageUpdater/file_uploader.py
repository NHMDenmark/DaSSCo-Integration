import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import mongo_connection, track_repository, metadata_repository
from StorageApi import storage_client
from Enums import validate_enum, status_enum
import InformationModule.slack_webhook as slack_webhook
import InformationModule.email_sender as email_sender
import utility
from InformationModule.log_class import LogClass
from HealthUtility import health_caller



"""
Responsible uploading files to open shares. Updates track database with assets status.
Logs warnings and errors from this process, and directs them to the health service. 
"""

class FileUploader(LogClass):

    def __init__(self):

        # setting up logging
        super().__init__(filename = f"{os.path.basename(os.path.abspath(__file__))}.log", name = os.path.relpath(os.path.abspath(__file__), start=project_root))
        # service name for logging/info purposes
        self.service_name = "File uploader ARS"

        self.track_mongo = track_repository.TrackRepository()
        self.metadata_mongo = metadata_repository.MetadataRepository()
        self.validate_enum = validate_enum.ValidateEnum
        self.status_enum = status_enum.StatusEnum
        self.slack_webhook = slack_webhook.SlackWebhook()
        self.email_sender = email_sender.EmailSender("test")
        self.util = utility.Utility()
        self.run_config_path = f"{project_root}/ConfigFiles/run_config.json"
        self.health_caller = health_caller.HealthCaller()

        # set the config file value to RUNNING, mostly for ease of testing
        self.util.update_json(self.run_config_path, self.service_name, self.status_enum.RUNNING.value)

        self.storage_api = self.create_storage_api()
        
        self.run = self.util.get_value(self.run_config_path, self.service_name)
        self.loop()

    """
    Creates the storage client.
    If this fails it sets the service run config to STOPPED and notifies the health service.  
    Returns the storage client or None. 
    """
    def create_storage_api(self):

        storage_api = storage_client.StorageClient()
         
        if storage_api.client is None:
            entry = self.log_exc(f"Failed to create storage client. {self.service_name} failed to run. Received status: {storage_api.status_code}. {self.service_name} needs to be manually restarted.", storage_api.exc, self.log_enum.ERROR.value)
            self.health_caller.warning(self.service_name, entry)
            self.run = self.util.update_json(self.run_config_path, self.service_name, self.status_enum.STOPPED.value)
            
        return storage_api

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            asset = self.track_mongo.get_entry_from_multiple_key_pairs([{"has_open_share" : self.validate_enum.YES.value, "has_new_file" : self.validate_enum.YES.value, "jobs_status" : self.status_enum.WAITING.value}])

            if asset is not None:
                guid = asset["_id"]
                # TODO check metadata exist handle fail, maybe this is too much checking - someone would have had to tamper with the db for this to not be there
                metadata = self.metadata_mongo.get_entry("_id", guid)
                # TODO handle if asset size is -1, something else went wrong since it should not be able to have this with the new files status set to YES
                if asset["asset_size"] != -1:

                    asset_files = asset["file_list"]

                    for file in asset_files:
                        
                        if file["erda_sync"] == validate_enum.ValidateEnum.NO.value:
                            
                            type = file["type"]
                            size = file["file_size"]
                            
                            file_path = f"{project_root}/Files/InProcess/" + asset["pipeline"] + "/" + asset["batch_list_name"][-10:] + "/" + guid + "/" + guid + "." + type

                            # check filepath exist and handle fail
                            if self.util.verify_path(file_path) is False:
                                self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.ERROR.value)
                                self.email_sender.send_error_mail(guid, "ars file uploader", self.validate_enum.ERROR.value, f"Expected file not found at: {file_path}")
                                self.slack_webhook.message_from_integration(guid, "ars file uploader", self.validate_enum.ERROR.value)
                                continue

                            uploaded, status = self.storage_api.upload_file(guid, metadata["institution"], metadata["collection"], file_path, size)

                            if uploaded is True:
                                self.track_mongo.update_entry(guid, "erda_sync", self.validate_enum.NO.value)
                                self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.AWAIT.value)
                            
                            # If we receive a message back saying the crc values for the uploaded file doesnt fit our value then we move the asset to the TEMP_ERROR status, send a mail and slack message
                            # TODO create a service that handles TEMP_ERROR status assets. 
                            if uploaded is False and status == 507:
                                self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.TEMP_ERROR.value)
                                self.email_sender.send_error_mail(guid, "ars file uploader", self.validate_enum.TEMP_ERROR.value, f"File failed to upload correctly due to crc failing to verify. Status: {status}")
                                self.slack_webhook.message_from_integration(guid, "ars file uploader", self.validate_enum.TEMP_ERROR.value)

                            # In case of an unforeseen issue the service will set its run config to False, send a mail and slack message about the error
                            # TODO implement a less decisive way of handling this (maybe)
                            # TODO implement a test run after setting "run" to false
                            if uploaded is False and status != 507:
                                self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.ERROR.value)
                                self.email_sender.send_error_mail(guid, "ars file uploader", self.validate_enum.ERROR.value, status)
                                self.slack_webhook.message_from_integration(guid, "ars file uploader", self.validate_enum.ERROR.value)
                                self.util.update_json(self.run_config_path, self.service_name, self.status_enum.STOPPED.value)
    
                        time.sleep(1)

            if asset is None:
                time.sleep(10)

            # checks if service should keep running - configurable in ConfigFiles/run_config.json            
            all_run = self.util.get_value(self.run_config_path, "all_run")
            service_run = self.util.get_value(self.run_config_path, self.service_name)

            # Pause loop
            counter = 0
            while service_run == self.status_enum.PAUSED.value:
                sleep = 10
                counter += 1
                time.sleep(sleep)
                wait_time = sleep * counter
                entry = self.log_msg(f"{self.service_name} has been in pause mode for ~{wait_time} seconds")
                self.health_caller.warning(self.service_name, entry)
                service_run = self.util.get_value(self.run_config_path, self.service_name)
                
                all_run = self.util.get_value(self.run_config_path, "all_run")
                if all_run == self.status_enum.STOPPED.value:
                    service_run = self.status_enum.STOPPED.value
                
                if service_run != self.status_enum.PAUSED.value:
                    entry = self.log_msg(f"{self.service_name} has changed run status from {self.status_enum.PAUSED.value} to {service_run}")                   
                    self.health_caller.warning(self.service_name, entry)

            if all_run == self.status_enum.STOPPED.value or service_run == self.status_enum.STOPPED.value:
                self.run = self.status_enum.STOPPED.value
        
        # Outside main while loop
        self.track_mongo.close_connection()
        self.metadata_mongo.close_connection()

if __name__ == '__main__':
    FileUploader()