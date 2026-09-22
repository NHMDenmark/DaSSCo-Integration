import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from datetime import datetime, timedelta
from Enums import validate_enum, status_enum, flag_enum, asset_status_nt
from IntegrationServer.StorageApi import storage_client
from HealthUtility import health_caller, run_utility
from MongoDB import service_repository

class UtilStorageAPI():

    def __init__(self, prefix_id, service_name, run_util: run_utility.RunUtility, mongo_client):

        self.prefix_id = prefix_id
        self.service_name = service_name
        self.run_util = run_util

        self.validate_enum = validate_enum.ValidateEnum
        self.status_enum = status_enum.StatusEnum
        self.flag_enum = flag_enum.FlagEnum
        self.asset_status_nt = asset_status_nt.AssetStatusNT

        self.service_mongo = service_repository.ServiceRepository(mongo_client)

        self.health_caller = health_caller.HealthCaller()

        self.auth_timestamp = None

        self.run = None

    """
    Creates the storage client.
    If this fails it sets the service run config to STOPPED and notifies the health service.  
    Returns the storage client or None.
    """
    def create_storage_api(self):
    
        storage_api = storage_client.StorageClient()
        
        self.auth_timestamp = datetime.now()

        self.run = self.run_util.get_service_run_status()

        # handle initial fails
        if storage_api.client is None and self.run != self.status_enum.STOPPED.value:
            # log the failure to create the storage api
            entry = self.run_util.log_exc(self.prefix_id, f"Failed to create storage client for {self.service_name}. Received status: {storage_api.status_code}. {self.service_name} will retry in 1 minute. {storage_api.note}",
                                           storage_api.exc, self.status_enum.ERROR.value)
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
                                           storage_api.exc, self.status_enum.ERROR.value)
            self.health_caller.error(self.service_name, entry)
            return storage_api
        
        return storage_api

    # check if new keycloak auth is needed, makes call to create the storage client
    def authorization_check(self, storage_api: storage_client.StorageClient):
        current_time = datetime.now()
        time_difference = current_time - self.auth_timestamp
                    
        if time_difference > timedelta(minutes=4):
            print(f"Keycloak auth expired for {self.service_name}. Attempting to create new storage client.")
            storage_api.service.metadata_db.close_connection()
            storage_api = self.create_storage_api()
            
        if storage_api.client is None:
            time.sleep(60)
            print("Waited 60 seconds before retrying to create the storage client after failing once")                
            storage_api = self.create_storage_api()

        return storage_api