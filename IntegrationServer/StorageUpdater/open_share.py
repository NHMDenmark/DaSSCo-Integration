import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from MongoDB import track_repository, metadata_repository, service_repository, throttle_repository
from StorageApi import storage_client
from Enums import status_enum, validate_enum
from Enums.status_enum import Status
from Enums.validate_enum import Validate
import utility
import time
from datetime import datetime, timedelta
from HealthUtility import health_caller, run_utility
from StorageApi import storage_client

"""
TODO Description
"""

class OpenShare(Status, Validate):

    def __init__(self):
        Status.__init__(self)
        Validate.__init__(self)

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        # service name for logging/info purposes
        self.service_name = "Open file share ARS"
        self.prefix_id = "OfsA"
        self.throttle_config_path = f"{project_root}/ConfigFiles/throttle_config.json"
        self.auth_timestamp = None
        self.mongo_track = track_repository.TrackRepository()
        self.mongo_metadata = metadata_repository.MetadataRepository()
        self.service_mongo = service_repository.ServiceRepository()
        self.throttle_mongo = throttle_repository.ThrottleRepository()
        self.util = utility.Utility()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum
        
        self.max_total_asset_size = self.util.get_value(self.throttle_config_path, "total_max_asset_size_mb")

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
            
            # check throttle
            total_size = self.throttle_mongo.get_value_for_key("total_max_asset_size_mb", "value")
            if total_size >= self.max_total_asset_size:
                # TODO implement better throttle than sleep
                time.sleep(5)
                self.end_of_loop_checks()
                continue
            
            print(f"total amount in system: {total_size}/{self.max_total_asset_size}")

            asset = self.mongo_track.get_entry_from_multiple_key_pairs([{"hpc_ready": self.NO, "has_open_share": self.NO,
                                                                          "jobs_status": self.WAITING, "is_in_ars": self.YES,
                                                                            "has_new_file": self.NO, "erda_sync": self.YES}])
            if asset is None:
                time.sleep(1)        
            else: 
                 
                guid = asset["_id"]
                institution = self.mongo_metadata.get_value_for_key(guid, "institution")
                collection = self.mongo_metadata.get_value_for_key(guid, "collection")
                asset_size = self.mongo_track.get_value_for_key(guid, "asset_size")
                
                proxy_path, status_code = self.storage_api.open_share(guid, institution, collection, asset_size)
                
                if proxy_path is not False:

                    self.mongo_track.update_entry(guid, "proxy_path", proxy_path)
                    
                    # create links for all files in the asset
                    files = asset["file_list"]

                    for file in files:
                        if file["deleted"] is not True:
                            name = file["name"]
                            link = proxy_path + name
                            self.mongo_track.update_track_file_list(guid, name, "ars_link", link)

                    self.update_throttle(asset)
                    self.mongo_track.update_entry(guid, "has_open_share", self.YES)

                if proxy_path is False:

                    if status_code == 504:
                        check = self.handle_status_504(guid, status_code)

                        if check is True:
                            self.update_throttle(asset)
                            self.mongo_track.update_entry(guid, "has_open_share", self.YES)
                        else:
                            self.handle_failures(guid, status_code)

                    # other failures    
                    else:
                        self.handle_failures(guid, status_code)

                    time.sleep(1)
                # TODO handle if proxy path is false
            
            self.end_of_loop_checks()

        # outside main while loop        
        self.mongo_track.close_connection()
        self.mongo_metadata.close_connection()
        self.service_mongo.close_connection()
        self.throttle_mongo.close_connection()

    def handle_failures(self, guid, status_code):
        entry = self.run_util.log_msg(self.prefix_id, f"Failed opening share for guid: {guid} Received status: {status_code}", self.ERROR)
        self.health_caller.error(self.service_name, entry, guid, "has_open_share", self.ERROR)
        self.mongo_track.update_entry(guid, "has_open_share", self.ERROR)

    def handle_status_504(self, guid, status_code):
        
        try:
            full_status = self.storage_api.get_full_asset_status(guid)

            if full_status["data"].status == "COMPLETED" and full_status["data"].share_allocation_mb != 0:
                entry = self.run_util.log_msg(self.prefix_id, f"Received status {status_code} for {guid}. Checked and the share was opened anyway.", self.run_util.log_enum.WARNING.value)
                self.health_caller.warning(self.service_name, entry, guid)
                return True
            
            else:
                return False

        except Exception as e:
            entry = self.run_util.log_exc(self.prefix_id, f"Failed to receive the status of asset {guid} while checking a status {status_code}.", e, self.ERROR)
            self.health_caller.error(self.service_name, entry, guid)
            return False
        

    def end_of_loop_checks(self):
        # checks if service should keep running          
        self.run = self.run_util.check_run_changes()

        # Pause loop
        if self.run == self.PAUSED:
            self.run = self.run_util.pause_loop()

    def update_throttle(self, asset):
        self.throttle_mongo.add_to_amount("total_max_asset_size_mb", "value", asset["asset_size"])

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
    OpenShare()