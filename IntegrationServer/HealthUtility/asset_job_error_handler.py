import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from datetime import datetime, timedelta
import utility
from MongoDB import service_repository, track_repository, metadata_repository, mos_repository, health_repository, throttle_repository
from HealthUtility import health_caller, run_utility
from Enums import status_enum, validate_enum, flag_enum, erda_status
from StorageApi import storage_client

"""
# Handles jobs that have gotten an error status. Either setting their status to RETRY or CRITICAL_ERROR depending on the situation.
"""
class AssetJobErrorHandler():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        self.pid = os.getpid()
        # service name for logging/info purposes
        self.service_name = "Asset job error handler"
        self.prefix_id= "Ajeh"

        self.util = utility.Utility()
        self.auth_timestamp = None
        self.service_mongo = service_repository.ServiceRepository()
        self.track_mongo = track_repository.TrackRepository()
        self.metadata_mongo = metadata_repository.MetadataRepository()
        self.mos_mongo = mos_repository.MOSRepository()
        self.health_mongo = health_repository.HealthRepository()
        self.health_caller = health_caller.HealthCaller()
        self.throttle_mongo = throttle_repository.ThrottleRepository()
        self.status_enum = status_enum.StatusEnum
        self.flag_enum = flag_enum.FlagEnum
        self.erda_enum = erda_status.ErdaStatusEnum
        self.validate_enum = validate_enum.ValidateEnum
        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name, self.pid)

        self.run_util.service_starting_updates()        
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        # create the storage api
        self.storage_api = self.create_storage_api()

        self.run = self.run_util.get_service_run_status()
        
        try:
            self.loop()
        except Exception as e:
            print("service crashed", e)
            try:
                entry = self.run_util.log_exc(self.prefix_id, f"{self.service_name} crashed.", e)
                self.health_caller.unexpected_error(self.service_name, entry)
            except:
                print(f"failed to inform about crash")
            self.run_util.service_stopping_updates()
            self.close_connections()


    def loop(self):

        while self.run == self.status_enum.RUNNING.value:

            assets = self.track_mongo.get_entries(self.flag_enum.JOBS_STATUS.value, self.status_enum.ERROR.value)

            if len(assets) == 0:
                time.sleep(300)

            for asset in assets:

                guid = asset["_id"]
                error_job = self.track_mongo.get_job_from_key_value(guid, "status", self.status_enum.ERROR.value)

                # TODO close shares and handle throttle counts if critical error
                if error_job is None:
                    entry = self.run_util.log_msg(self.prefix_id, f"Asset {guid} had jobs_status {self.status_enum.ERROR.value} but no job with status {self.status_enum.ERROR.value} was found. Setting asset jobs_status to {self.status_enum.CRITICAL_ERROR.value}.")
                    self.health_caller.error(self.service_name, entry, guid, self.flag_enum.JOBS_STATUS.value, self.status_enum.CRITICAL_ERROR.value)
                    self.track_mongo.update_entry(guid, self.flag_enum.JOBS_STATUS.value, self.status_enum.CRITICAL_ERROR.value)
                    self.track_mongo.update_entry(guid, self.flag_enum.AVAILABLE_FOR_SERVICES.value, self.validate_enum.NO.value)
                    continue
                # TODO close shares and handle throttle counts if critical error
                third_job_fail = self.track_mongo.get_job_from_key_value(guid, "name", f"attempt_2_{error_job["name"]}")
                if third_job_fail is not None:
                    entry = self.run_util.log_msg(self.prefix_id, f"Asset {guid} had job {error_job['name']} fail for the third time. Setting asset jobs_status to {self.status_enum.CRITICAL_ERROR.value}.")
                    self.health_caller.error(self.service_name, entry, guid, self.flag_enum.JOBS_STATUS.value, self.status_enum.CRITICAL_ERROR.value)
                    self.track_mongo.update_entry(guid, self.flag_enum.JOBS_STATUS.value, self.status_enum.CRITICAL_ERROR.value)
                    self.track_mongo.update_entry(guid, self.flag_enum.AVAILABLE_FOR_SERVICES.value, self.validate_enum.NO.value)
                    continue

                if error_job["name"] == "assetLoader":
                    self.handle_asset_loader_error(asset, guid, error_job)

                if error_job["name"] == "barcode":
                    self.handle_barcode_error(asset, guid, error_job)

                if error_job["name"] == "cropping":
                    self.handle_cropping_error(asset, guid, error_job)

                if error_job["name"] == "derivative":
                    self.handle_derivative_error(asset, guid, error_job)

                if error_job["name"] == "uploader":
                    self.handle_uploader_error(asset, guid, error_job)

                if error_job["name"] == "clean_up":
                    self.handle_clean_up_error(asset, guid, error_job)
            
            # TODO remove or lower for prod
            time.sleep(200)

            #checks if service should keep running           
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.status_enum.PAUSED.value:
                self.run = self.run_util.pause_loop()
        
        # out of main loop
        self.run_util.service_stopping_updates()
        self.close_connections()
        print("Service shut down")

    ### TODO implement the handlers below ###
    def handle_asset_loader_error(self, asset, guid, error_job):
        
        self.authorization_check()
        if self.storage_api is None:
                return
        pass

    def handle_barcode_error(self, asset, guid, error_job):
        
        pass

    def handle_cropping_error(self, asset, guid, error_job):
        
        pass

    def handle_derivative_error(self, asset, guid, error_job):

        pass
    
    # TODO handle other cases
    def handle_uploader_error(self, asset, guid, error_job):
        
        metadata = self.metadata_mongo.get_entry("_id", guid)
        institution = metadata["institution"]
        collection = metadata["collection"]
        
        self.authorization_check()
        if self.storage_api is None:
                return
        
        ars_status = self.storage_api.get_full_asset_status(guid)
        ars_file_list = self.storage_api.get_files_available(guid, institution, collection)

        if ars_status is False or ars_file_list is False:
            return

        # set retry status if no file found in ARS
        if ars_status["data"].status == self.erda_enum.METADATA_RECEIVED.value and len(ars_file_list["data"]) == 1 and ars_status["data"].share_allocation == asset["asset_size"] and ars_status["data"].error_message is None:
            self.track_mongo.update_entry(guid, self.flag_enum.JOBS_STATUS.value, self.status_enum.RETRY.value)
            self.track_mongo.update_track_job_status(guid, error_job["name"], self.status_enum.RETRY.value)
            return
        
        # return asset to normal flow if fully uploaded to ARS
        if ars_status["data"].status == self.erda_enum.METADATA_RECEIVED.value and len(ars_file_list["data"]) == 2 and ars_status["data"].share_allocation == asset["asset_size"] and ars_status["data"].error_message is None:
            self.track_mongo.update_entry(guid, self.flag_enum.AVAILABLE_FOR_SERVICES.value, self.validate_enum.NO.value)
            self.track_mongo.update_entry(guid, self.flag_enum.JOBS_STATUS.value, self.status_enum.WAITING.value)
            self.track_mongo.update_track_job_status(guid, error_job["name"], self.status_enum.DONE.value)
            self.track_mongo.update_entry(guid, self.flag_enum.HAS_NEW_FILE.value, self.validate_enum.AWAIT.value)

            for file in ars_file_list["data"]:
                for ext in [".tif", ".jpeg"]:
                    expected_name = guid + ext
                    if expected_name in file:
                        self.track_mongo.update_track_file_list(guid, expected_name, "ars_link", file)
                        self.track_mongo.update_entry(guid, "proxy_path", file)

            entry = self.run_util.log_msg(self.prefix_id, f"Asset {guid} had job {error_job['name']} in error state. However the asset is fully uploaded to ARS. Setting jobs_status to {self.status_enum.WAITING.value} and has_new_file to {self.validate_enum.AWAIT.value}.")
            self.health_caller.warning(self.service_name, entry, guid, self.flag_enum.JOBS_STATUS.value, self.status_enum.WAITING.value)
            self.track_mongo.update_entry(guid, self.flag_enum.AVAILABLE_FOR_SERVICES.value, self.validate_enum.YES.value)
            return

        return

    def handle_clean_up_error(self, asset, guid, error_job):
        
        pass

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
            print(f"creating new storage client, after {time_difference}")
            self.storage_api = self.create_storage_api()
        if self.storage_api.client is None:
            time.sleep(60)
            print("Waited 60 seconds before retrying to create the storage client after failing once")                
            self.storage_api = self.create_storage_api()

    def subtract_from_assets_in_flight(self):
        self.throttle_mongo.subtract_one_from_count("assets_in_flight", "value")

    def subtract_asset_size_from_key(self, asset, key):
        size = asset["asset_size"]
        self.throttle_mongo.subtract_from_amount(key, "value", size)

    def subtract_asset_total_size(self, asset):
        size = asset["total_size"]
        self.throttle_mongo.subtract_from_amount("total_asset_size_mb", "value", size)
        
    def close_connections(self):
        try:
            self.service_mongo.close_connection()
            self.track_mongo.close_connection()
            self.metadata_mongo.close_connection()
            self.mos_mongo.close_connection()
            self.health_mongo.close_connection()
            self.throttle_mongo.close_connection()
        except Exception as e:
            print(e)

if __name__ == '__main__':
    AssetJobErrorHandler()