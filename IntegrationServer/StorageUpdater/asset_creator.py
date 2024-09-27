import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import threading
import time
from datetime import datetime, timedelta
from MongoDB import metadata_repository, track_repository, service_repository, throttle_repository
from StorageApi import storage_client
from Enums import validate_enum, status_enum, erda_status
from HealthUtility import health_caller, run_utility
import utility

"""
Responsible creating new metadata assets in ars. Updates track database with assets status.
Logs warnings and errors from this process, and directs them to the health service. 
"""
class AssetCreator():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        
        self.service_name = "Asset creator ARS"
        self.prefix_id = "AcA"
        self.auth_timestamp = None
        self.throttle_config_path = f"{project_root}/ConfigFiles/throttle_config.json"
        self.track_mongo = track_repository.TrackRepository()
        self.metadata_mongo = metadata_repository.MetadataRepository()
        self.service_mongo = service_repository.ServiceRepository()
        self.throttle_mongo = throttle_repository.ThrottleRepository()
        self.health_caller = health_caller.HealthCaller()
        self.validate_enum = validate_enum.ValidateEnum
        self.status_enum = status_enum.StatusEnum
        self.erda_status_enum = erda_status.ErdaStatusEnum
        self.util = utility.Utility()

        self.max_total_asset_size = self.util.get_value(self.throttle_config_path, "total_max_asset_size_mb")
        self.max_new_asset_size = self.util.get_value(self.throttle_config_path, "total_max_new_asset_size_mb")
        self.max_derivative_size = self.util.get_value(self.throttle_config_path, "total_max_derivative_size_mb")

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
        
        # create and start the heartbeat thread
        heartbeat_thread = threading.Thread(target = self.heartbeat)
        heartbeat_thread.start()

        self.loop()

    """
    Main loop for the service.
    """
    def loop(self):
        
        while self.run == self.status_enum.RUNNING.value:
            
            # check if new keycloak auth is needed, creates the storage client
            self.authorization_check()
            if self.storage_api is None:
                continue

            # check throttle
            new_asset, derivative_asset, total_size = self.check_throttle()
            
            if total_size >= self.max_total_asset_size:
                # TODO implement better throttle than sleep
                time.sleep(5)
                self.end_of_loop_checks()
                continue

            print(f"total amount in system: {total_size}/{self.max_total_asset_size}")

            # TODO this is dangerous. Using the jobs status to logically assume its a derivative. Maybe track needs a new field
            if new_asset is False:
                asset = self.track_mongo.get_entry_from_multiple_key_pairs([{"is_in_ars" : self.validate_enum.NO.value, "jobs_status" : self.status_enum.DONE.value}])
            # TODO this is dangerous. Using the jobs status to logically assume its a new asset. Maybe track needs a new field
            if derivative_asset is False:
                asset = self.track_mongo.get_entry_from_multiple_key_pairs([{"is_in_ars" : self.validate_enum.NO.value, "jobs_status" : self.status_enum.WAITING.value}])

            if new_asset and derivative_asset:
                asset = self.track_mongo.get_entry("is_in_ars", self.validate_enum.NO.value)                

            if asset is not None:
                guid = asset["_id"]                
                
                # Receives created: bool, response: str, exc: exception, status_code: int
                if asset["asset_size"] != -1:
                    created, response, exc, status_code = self.storage_api.create_asset(guid, asset["asset_size"])
                else:
                    created, response, exc, status_code = self.storage_api.create_asset(guid)

                # success scenario for creating the asset in ARS
                if created is True:
                    self.handle_throttle(asset)
                    self.success_asset_created(guid, asset)

                # fail scenarios
                if created is False:
                    # handles if status code is a negative number - this means we set it during another exception - see storage_client.get_status_code_from_exc()
                    if status_code < 0: 
                        message = self.run_util.log_exc(self.prefix_id, response, exc, self.run_util.log_enum.ERROR.value)
                        self.health_caller.error(self.service_name, message, guid, "is_in_ars", self.validate_enum.ERROR.value)

                    if 200 <= status_code <= 299:                    
                        message = self.run_util.log_msg(self.prefix_id, response)
                        self.health_caller.warning(self.service_name, message)
                        # TODO check if asset exists in ARS, add to throttle value
                        
                    # TODO handle 300-399?

                    if status_code > 299 and status_code != 504:
                        print(f"{guid} failed to create and got status {status_code}")

                    if 400 <= status_code <= 499:
                        message = self.run_util.log_exc(self.prefix_id, response, exc, self.run_util.log_enum.ERROR.value)
                        #self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.PAUSED.value)
                        self.health_caller.warning(self.service_name, message, guid, "is_in_ars", self.validate_enum.PAUSED.value)
                        time.sleep(1)
                    
                    if 500 <= status_code <= 502 or 505 <= status_code <= 599: 
                        message = self.run_util.log_exc(self.prefix_id, response, exc)
                        #self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.PAUSED.value)
                        self.health_caller.warning(self.service_name, message, guid, "is_in_ars", self.validate_enum.ERROR.value)
                        time.sleep(1)
                    if status_code == 503:
                        message = self.run_util.log_msg(self.prefix_id, response)
                        self.health_caller.warning(self.service_name, message, guid, "is_in_ars", self.validate_enum.PAUSED.value)
                        self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.NO.value)

                    # handle status 504, this can happen while the asset successfully is created if ARS internal communication broken down.
                    if status_code == 504:
                        print(f"{guid} got time out status: {status_code} Checking if asset was created.")
                        try:
                            exists = self.storage_api.get_asset_status(guid)

                            # TODO might want to add some kind of pausing if too many timeouts happe
                            # logs the timeout failure, does not update the asset flags -> asset will be retried
                            if exists == False:                                
                                message = self.run_util.log_msg(self.prefix_id, f"Timeout detected without creating {guid}. Status: {status_code}. {response}")
                                self.health_caller.warning(self.service_name, message, guid)

                            if exists == self.erda_status_enum.METADATA_RECEIVED.value:
                                # success anyway
                                self.success_asset_created(guid, asset)
                                self.handle_throttle(asset)
                                # log the time out
                                message = self.run_util.log_msg(self.prefix_id, f"{guid} was created despite receiving status {status_code} from ARS. {response}")
                                self.health_caller.warning(self.service_name, message, guid)

                        except Exception as e:
                            message = self.run_util.log_exc(self.prefix_id, response, exc, self.run_util.log_enum.ERROR.value)                            
                            self.health_caller.warning(self.service_name, message, guid, "is_in_ars", self.validate_enum.ERROR.value)

                time.sleep(1)

            if asset is None:
                time.sleep(10)

            self.end_of_loop_checks()

        # outside main while loop        
        self.track_mongo.close_connection()
        self.metadata_mongo.close_connection()
        self.service_mongo.close_connection()
        self.throttle_mongo.close_connection()
        self.run_util.service_mongo.close_connection()
        self.storage_api.service.metadata_db.close_mdb()
        print("service stopped")

    def success_asset_created(self, guid, asset):
        metadata = self.metadata_mongo.get_entry("_id", guid)
        self.track_mongo.update_entry(guid, "is_in_ars", self.validate_enum.YES.value)
        self.track_mongo.update_entry(guid, "has_open_share", self.validate_enum.YES.value)
        if asset["asset_size"] != -1:
            self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.YES.value)

    def handle_throttle(self, asset):
        
        is_derivative = self.is_asset_derivative(asset["_id"])
        
        self.throttle_mongo.add_to_amount("total_max_asset_size_mb", "value", asset["asset_size"])

        if is_derivative is False:
            self.throttle_mongo.add_to_amount("total_max_new_asset_size_mb", "value", asset["asset_size"])
        else:
            self.throttle_mongo.add_to_amount("total_max_derivative_size_mb", "value", asset["asset_size"])

    # end of loop checks
    def end_of_loop_checks(self):
        # checks if service should keep running           
        self.run = self.run_util.check_run_changes()

        # Pause loop
        if self.run == self.validate_enum.PAUSED.value:
            self.run = self.run_util.pause_loop()
    
    """
    Checks the throttle and sends back bools for new asset and derivative that tells if they can be used. Also sends back the total amount in the system.     
    """
    def check_throttle(self):
        
            total_size = self.throttle_mongo.get_value_for_key("total_max_asset_size_mb", "value")
            new_asset_size = self.throttle_mongo.get_value_for_key("total_new_asset_size_mb", "value")
            derivative_asset_size = self.throttle_mongo.get_value_for_key("total_derivative_asset_size_mb", "value")
            
            new_asset = True
            derivative_asset = True
            if new_asset_size >= self.max_new_asset_size:
                new_asset = False
            if derivative_asset_size >= self.max_derivative_size:
                derivative_asset = False
            
            return new_asset, derivative_asset, total_size
    
    #check if an asset is a derivative by checking if it has a parent
    def is_asset_derivative(self, guid):
        value = self.metadata_mongo.get_value_for_key(guid, "parent_guid")
        if value is None or value == "":
            return False
        else:
            return True

    """
    Thread running the "heartbeat" loop for the healthservice to check in on. 
    Stops if the run_status in the micro service database is set to STOPPED.
    """
    # TODO decide how this will actually be implemented with the 3rd party health service
    def heartbeat(self):
            while self.run != self.status_enum.STOPPED.value:
                time.sleep(10)
                try:
                    self.run = self.run_util.check_run_changes()
                    if self.run == self.status_enum.STOPPED.value:
                        print("im dead")
                    elif self.run == self.status_enum.PAUSED.value:
                        print("im asleep")
                    else:
                        print("im alive")
                except:
                    print("im dead")
                    
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
    
    AssetCreator()