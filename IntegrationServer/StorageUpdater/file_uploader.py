import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from datetime import datetime, timedelta
from MongoDB import track_repository, metadata_repository, service_repository
from StorageApi import storage_client
from Enums import validate_enum, status_enum
import InformationModule.slack_webhook as slack_webhook
import InformationModule.email_sender as email_sender
import utility
from HealthUtility import health_caller, run_utility

"""
Responsible uploading files to open shares. Updates track database with assets status.
Logs warnings and errors from this process, and directs them to the health service. 
"""

class FileUploader():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)

        self.service_name = "File uploader ARS"
        self.prefix_id = "FuA"
        self.auth_timestamp = None
        self.track_mongo = track_repository.TrackRepository()
        self.metadata_mongo = metadata_repository.MetadataRepository()
        self.service_mongo = service_repository.ServiceRepository()
        self.validate_enum = validate_enum.ValidateEnum
        self.status_enum = status_enum.StatusEnum
        self.slack_webhook = slack_webhook.SlackWebhook()
        self.email_sender = email_sender.EmailSender("test")
        self.util = utility.Utility()
        self.health_caller = health_caller.HealthCaller()

        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name)

        # set the service db value to RUNNING, mostly for ease of testing
        self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.RUNNING.value)
        # special status change, logging and contact health api
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        # get currrent self.run value
        self.run = self.run_util.get_service_run_status()
        # update service_run value for run_util
        self.run_util.service_run = self.run

        # create the storage api
        self.storage_api = self.create_storage_api()
        
        try:
            self.loop()
        except Exception as e:
            print("service crashed", e)

    """
    Creates the storage client.
    If this fails it sets the service run config to STOPPED and notifies the health service.  
    Returns the storage client or None.
    """
    def create_storage_api(self):
    
        storage_api = storage_client.StorageClient()
        
        self.auth_timestamp = datetime.now()

        # handle initial fails
        if storage_api.client is None and self.run != self.status_enum.STOPPED.value:
            # log the failure to create the storage api
            entry = self.run_util.log_exc(self.prefix_id, f"Failed to create storage client for {self.service_name}. Received status: {storage_api.status_code}. {self.service_name} will retry in 1 minute. {storage_api.note}",
                                           storage_api.exc, self.run_util.log_enum.ERROR.value)
            self.health_caller.error(self.service_name, entry)

            # change run value in db 
            self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.STOPPED.value)
            
            # log the status change + health call 
            self.run_util.log_status_change(self.service_name, self.run, self.status_enum.STOPPED.value)

            # update run values
            self.run = self.run_util.get_service_run_status()
            self.run_util.service_run = self.run

            return storage_api           
        
        # handle retry success
        if storage_api.client is not None and self.run == self.status_enum.STOPPED.value:            
            
            entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} created storage client after retrying.")
            self.health_caller.warning(self.service_name, entry)

            # change run value in db 
            self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.RUNNING.value)
            
            # log the status change + health call
            self.run_util.log_status_change(self.service_name, self.run, self.status_enum.RUNNING.value)

            # update run values
            self.run = self.run_util.get_service_run_status()
            self.run_util.service_run = self.run

            return storage_api

        # handles retry fail
        if storage_api.client is None and self.run == self.status_enum.STOPPED.value:
            entry = self.run_util.log_exc(self.prefix_id, f"Retry failed to create storage client for {self.service_name}. Received status: {storage_api.status_code}. {self.service_name} will shut down and need to be restarted manually. {storage_api.note}",
                                           storage_api.exc, self.run_util.log_enum.ERROR.value)
            self.health_caller.error(self.service_name, entry)
            return storage_api
        
        return storage_api
    

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            # check if new keycloak auth is needed, creates the storage client
            self.authorization_check()
            if self.storage_api is None:
                continue

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
                                self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.PAUSED.value)
                                self.email_sender.send_error_mail(guid, "ars file uploader", self.validate_enum.PAUSED.value, f"File failed to upload correctly due to crc failing to verify. Status: {status}")
                                self.slack_webhook.message_from_integration(guid, "ars file uploader", self.validate_enum.PAUSED.value)

                            # In case of an unforeseen issue the service will set its run config to False, send a mail and slack message about the error
                            # TODO implement a less decisive way of handling this (maybe)
                            # TODO implement a test run after setting "run" to false
                            if uploaded is False and status != 507:
                                self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.ERROR.value)
                                self.email_sender.send_error_mail(guid, "ars file uploader", self.validate_enum.ERROR.value, status)
                                self.slack_webhook.message_from_integration(guid, "ars file uploader", self.validate_enum.ERROR.value)                                
    
                        time.sleep(1)

            if asset is None:
                time.sleep(10)

            # checks if service should keep running           
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.validate_enum.PAUSED.value:
                self.run = self.run_util.pause_loop()
        
        # Outside main while loop
        self.track_mongo.close_connection()
        self.metadata_mongo.close_connection()
        self.service_mongo.close_connection()
        print("Service stopped")

    # check if new keycloak auth is needed, makes call to create the storage client
    def authorization_check(self):
        current_time = datetime.now()
        time_difference = current_time - self.auth_timestamp
            
        if time_difference > timedelta(minutes=4):
            self.storage_api.service.metadata_db.close_mdb()
            print(f"creating new storage client, after {time_difference}")
            self.storage_api = self.create_storage_api()
        if self.storage_api.client is None:
            time.sleep(60)
            print("Waited 60 seconds before retrying to create the storage client after failing once")                
            self.storage_api = self.create_storage_api()

if __name__ == '__main__':
    FileUploader()