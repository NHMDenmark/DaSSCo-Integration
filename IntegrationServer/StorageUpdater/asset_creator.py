import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import mongo_connection
from StorageApi import storage_client
from Enums import validate_enum
from InformationModule.log_class import LogClass
from HealthUtility import health_caller
import utility


"""
Responsible creating new metadata assets in ars.
"""

class AssetCreator(LogClass):

    def __init__(self):

        # setting up logging
        super().__init__(filename = f"{os.path.basename(os.path.abspath(__file__))}.log", name = os.path.basename(os.path.abspath(__file__)))
        # service name for logging/info purposes
        self.service_name = "Asset creator ARS"

        self.track_mongo = mongo_connection.MongoConnection("track")
        self.metadata_mongo = mongo_connection.MongoConnection("metadata")
        self.health_caller = health_caller.HealthCaller()
        self.validate_enum = validate_enum.ValidateEnum
        self.util = utility.Utility()
        self.run = True

        self.storage_api = storage_client.StorageClient()
        
        if self.storage_api.client is None:
            entry = self.log_exc(f"Failed to create storage client. {self.service_name} failed to run. Received status: {self.storage_api.status_code}. {self.service_name} needs to be manually restarted.", self.storage_api.exc, self.log_enum.ERROR.value)
            self.health_caller.warning(self.service_name, entry)
            self.run = False

        self.loop()

    def loop(self):

        while self.run:
            
            asset = self.track_mongo.get_entry("is_in_ars", self.validate_enum.NO.value)

            if asset is not None:
                guid = asset["_id"]
                
                if asset["asset_size"] != -1:
                    created, response, exc, status_code = self.storage_api.create_asset(guid, asset["asset_size"])
                else:
                    created, response, exc, status_code = self.storage_api.create_asset(guid)


                if created is True:
                    metadata = self.metadata_mongo.get_entry("_id", guid)
                    self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.YES.value)
                    self.track_mongo.update_entry(guid, "has_open_share", self.validate_enum.YES.value)
                    if asset["asset_size"] != -1 and metadata["parent_guid"] == "":
                        self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.YES.value)

                if created is False:
                    if status_code <= 399:                    
                        message = self.log_msg(response)

                    if 400 <= status_code <= 499:
                        message = self.log_exc(response, exc, self.log_enum.ERROR.value)
                        self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.TEMP_ERROR.value)
                        self.health_caller.warning(self.service_name, message, guid, "is_in_ars")
                        time.sleep(1)
                    if 500 <= status_code:
                        message = self.log_exc(response, exc)
                        self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.TEMP_ERROR.value)
                        self.health_caller.warning(self.service_name, message)
                        time.sleep(1)
                    # self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.ERROR.value) this responsibility is moved to health module, sets TEMP_ERROR status here 

                time.sleep(1)

            if asset is None:
                time.sleep(1)

            # checks if service should keep running - configurable in ConfigFiles/run_config.json
            run_config_path = f"{project_root}/ConfigFiles/run_config.json"
            
            all_run = self.util.get_value(run_config_path, "all_run")
            service_run = self.util.get_value(run_config_path, "asset_creator_run")

            # Pause loop
            counter = 0
            while service_run == "Pause":
                sleep = 10
                counter += 1
                time.sleep(sleep)
                wait_time = sleep * counter
                entry = self.log_msg(f"{self.service_name} has been in pause mode for ~{wait_time} seconds")
                self.health_caller.warning(self.service_name, entry)
                service_run = self.util.get_value(run_config_path, "asset_creator_run")
                if service_run != "Pause":
                    entry = self.log_msg(f"{self.service_name} has changed run status from 'Pause' to {service_run}")                   
                    self.health_caller.warning(self.service_name, entry)

            if all_run == "False" or service_run == "False":
                self.run = False

        # outside main while loop        
        self.track_mongo.close_mdb()
        self.metadata_mongo.close_mdb()

if __name__ == '__main__':
    AssetCreator()