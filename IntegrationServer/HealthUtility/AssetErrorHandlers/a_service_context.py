import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from datetime import datetime, timedelta
import utility
from MongoDB.mongo_connection import MongoSharedClient
from MongoDB import service_repository, track_repository, metadata_repository, mos_repository, health_repository, throttle_repository
from HealthUtility import health_caller, run_utility
from Enums import status_enum, validate_enum, flag_enum, erda_status, asset_status_nt
from StorageApi import storage_client

class ServiceContext:
    
    def __init__(self):
        self.pid = os.getpid()
        self.service_name = "Asset error status handler"
        self.prefix_id = "Aesh"

        self.mongo_client = MongoSharedClient()
        self.service_mongo = service_repository.ServiceRepository(self.mongo_client)
        self.track_mongo = track_repository.TrackRepository(self.mongo_client)
        self.metadata_mongo = metadata_repository.MetadataRepository(self.mongo_client)
        self.mos_mongo = mos_repository.MOSRepository(self.mongo_client)
        self.health_mongo = health_repository.HealthRepository(self.mongo_client)
        self.throttle_mongo = throttle_repository.ThrottleRepository(self.mongo_client)

        self.status_enum = status_enum.StatusEnum
        self.flag_enum = flag_enum.FlagEnum
        self.asset_status_enum = asset_status_nt.AssetStatusNT
        self.erda_enum = erda_status.ErdaStatusEnum
        self.validate_enum = validate_enum.ValidateEnum

        self.health_caller = health_caller.HealthCaller()
        self.util = utility.Utility()

        self.run_util = run_utility.RunUtility(
            self.prefix_id,
            self.service_name,
            f"asset_error_status_handler.py.log",
            __file__,
            self.pid,
            self.mongo_client
        )

        self.run = self.run_util.get_service_run_status()

        self.storage_api = self.create_storage_api()
    
    """
    Creates the storage client.
    If this fails it sets the service run config to STOPPED and notifies the health service.  
    Returns the storage client or None. 
    """
    def create_storage_api(self):
    
        storage_api = storage_client.StorageClient()
        
        self.auth_timestamp = datetime.now()

        if storage_api.client is None:
            # log the failure to create the storage api
            entry = self.run_util.log_exc(self.prefix_id, f"Failed to create storage client. {self.service_name} failed to run. Received status: {storage_api.status_code}. {self.service_name} needs to be manually restarted. {storage_api.note}",
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
    
    # check if new keycloak auth is needed, makes call to create the storage client
    def authorization_check(self):
        current_time = datetime.now()
        time_difference = current_time - self.auth_timestamp
            
        if time_difference > timedelta(minutes=4):
            self.storage_api.service.metadata_db.close_connection()
            # print(f"creating new storage client, after {time_difference}")
            self.storage_api = self.create_storage_api()
        if self.storage_api.client is None:
            time.sleep(60)
            print("Waited 60 seconds before retrying to create the storage client after failing once")                
            self.storage_api = self.create_storage_api()

    def close_connections(self):
        try:
            self.service_mongo.close_connection()
            self.track_mongo.close_connection()
            self.metadata_mongo.close_connection()
            self.mos_mongo.close_connection()
            self.health_mongo.close_connection()
            self.throttle_mongo.close_connection()
            self.mongo_client.close()
        except Exception as e:
            print(e)