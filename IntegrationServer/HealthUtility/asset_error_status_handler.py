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
from Enums import status_enum, validate_enum, flag_enum, erda_status, asset_status_nt
from StorageApi import storage_client

"""
# TODO Description Add in flight throttle count
"""
class AssetErrorStatusHandler():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        self.pid = os.getpid()
        # service name for logging/info purposes
        self.service_name = "Asset error status handler"
        self.prefix_id= "Aesh"

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
        self.asset_status_enum = asset_status_nt.AssetStatusNT
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
                entry = self.run_util.log_exc(self.prefix_id, f"{self.service_name} crashed.", e, self.status_enum.CRITICAL_ERROR.value)
                self.health_caller.unexpected_error(self.service_name, entry)
            except:
                print(f"failed to inform about crash")
            self.run_util.service_stopping_updates()
            self.close_connections()


    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            self.authorization_check()
            if self.storage_api is None:
                continue

            assets = self.track_mongo.get_error_entries()

            if assets is None:
                time.sleep(180)
            else:
                errors_found = 0
                for asset in assets:

                    # let asset_job_error_handler handle jobs_status errors
                    if asset["jobs_status"] == self.status_enum.ERROR.value:
                        continue

                    errors_found += 1
                    guid = asset["_id"]
                    
                    # erda_sync error
                    if asset[self.flag_enum.ERDA_SYNC.value] == self.status_enum.ERROR.value:
                        self.handle_erda_sync_error(asset, guid)

                    # has_open_share error
                    if asset[self.flag_enum.HAS_OPEN_SHARE.value] == self.status_enum.ERROR.value:
                        self.handle_has_open_share_error(asset, guid)

                    # specify_sync error
                    if asset[self.flag_enum.SPECIFY_SYNC.value] == self.status_enum.ERROR.value:
                        self.handle_specify_sync_error(asset, guid)

                print(f"Assets with errors found: {errors_found}")
                time.sleep(60)

            #checks if service should keep running           
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.status_enum.PAUSED.value:
                self.run = self.run_util.pause_loop()
        
        # out of main loop
        self.run_util.service_stopping_updates()
        self.close_connections()
        print("Service shut down")

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

    def handle_erda_sync_error(self, asset, guid):
        
        self.authorization_check()

        ars_status = self.storage_api.get_full_asset_status(guid)

        # gives time for ARS to update - in case this is about the share still appearing open despite sync completed
        time.sleep(120)

        if ars_status["data"].status == self.erda_enum.COMPLETED.value and ars_status["data"].share_allocation_mb is None:
            
            self.throttle_mongo.add_one_to_count("await_sync_asset_count", "value")
            self.track_mongo.update_entry(guid, self.flag_enum.ERDA_SYNC.value, self.validate_enum.AWAIT.value)
            print(f"found {guid} to have been successfully synced to erda - sent asset back to normal flow")
            self.run_util.update_metadata_status(guid, self.asset_status_enum.BEING_PROCESSED.value)

        else:
            print(f"unable to handle {guid} - set to critical error")
            message = self.run_util.log_msg(self.prefix_id, f"Tried handling erda_sync error for {guid}. Could not determine the issue. Will need manual handling. erda_sync set to {self.status_enum.CRITICAL_ERROR.value}")
            self.health_caller.error(self.service_name, message, guid, "erda_sync", self.status_enum.CRITICAL_ERROR.value)
            self.remove_asset_from_in_flight_count()
            self.run_util.update_metadata_status(guid, self.asset_status_enum.ERROR.value)

    def handle_has_open_share_error(self, asset, guid):
        
        self.authorization_check()

        ars_status = self.storage_api.get_full_asset_status(guid)

        if ars_status is False:
            print(f"unable to handle {guid} - set to critical error")
            self.track_mongo.update_entry(guid, self.flag_enum.HAS_OPEN_SHARE.value, self.status_enum.CRITICAL_ERROR.value)
            message = self.run_util.log_msg(self.prefix_id, f"Tried handling has_open_share error for {guid}. Could not determine the issue. Failed to get information about asset from ARS. has_open_share set to {self.status_enum.CRITICAL_ERROR.value}")
            self.health_caller.error(self.service_name, message, guid, "has_open_share", self.status_enum.CRITICAL_ERROR.value)
            self.remove_asset_from_in_flight_count()
            self.run_util.update_metadata_status(guid, self.asset_status_enum.ERROR.value)            
            return
        
        status = ars_status["data"].status
        share_allocation = ars_status["data"].share_allocation_mb
        error_message = ars_status["data"].error_message
        asset_available = asset[self.flag_enum.AVAILABLE_FOR_SERVICES.value]
        asset_erda_sync = asset[self.flag_enum.ERDA_SYNC.value]
        asset_size = asset["asset_size"]
        asset_jobs_status = asset["jobs_status"]
        asset_specify_sync = asset[self.flag_enum.SPECIFY_SYNC.value]
        institution = self.metadata_mongo.get_value_for_key(guid, "institution")
        collection = self.metadata_mongo.get_value_for_key(guid, "collection")

        # asset share was opened despite the status being sent back saying otherwise
        if share_allocation is not None and share_allocation == asset_size:
                    # asset has files available and share allocation exists - should be fine to move on
                    files = self.storage_api.get_files_available(guid, institution, collection)
                    if files is not False:
                        self.track_mongo.update_entry(guid, self.flag_enum.HAS_OPEN_SHARE.value, self.validate_enum.YES.value)
                        message = self.run_util.log_msg(self.prefix_id, f"Successfully handled has_open_share error for {guid}. Asset had share allocation match asset size. Asset files were found to be available in ARS. has_open_share set to {self.validate_enum.YES.value}")
                        self.health_caller.warning(self.service_name, message, guid, "has_open_share", self.validate_enum.YES.value)
                        self.run_util.update_metadata_status(guid, self.asset_status_enum.BEING_PROCESSED.value)
                        return

        if status == self.erda_enum.ERDA_SYNCHRONISED.value:

            # specify open share fails -> retry opening the share
            if asset_specify_sync == self.validate_enum.PREPARE.value:
                
                try:
                    proxy_path, status_code = self.storage_api.open_share(guid, institution, collection, asset_size)
                
                    if proxy_path is not False:

                        self.track_mongo.update_entry(guid, "proxy_path", proxy_path)
                        
                        # create links for all files in the asset
                        files = asset["file_list"]

                        for file in files:
                            if file["deleted"] is not True:
                                name = file["name"]
                                link = proxy_path + name
                                self.track_mongo.update_track_file_list(guid, name, "ars_link", link)

                        self.update_throttle_plus_size(asset)
                        self.track_mongo.update_entry(guid, "has_open_share", self.validate_enum.YES.value)
                        message = self.run_util.log_msg(self.prefix_id, f"Successfully handled has_open_share error for {guid}. has_open_share set to {self.validate_enum.YES.value}")
                        self.health_caller.warning(self.service_name, message, guid, "has_open_share", self.validate_enum.YES.value)
                        self.run_util.update_metadata_status(guid, self.asset_status_enum.BEING_PROCESSED.value)

                    elif proxy_path is False:                        
                        message = self.run_util.log_msg(self.prefix_id, f"Tried handling has_open_share error for {guid}. Failed to open share in ARS.", self.status_enum.CRITICAL_ERROR.value)
                        self.health_caller.warning(self.service_name, message, guid, "has_open_share", self.status_enum.CRITICAL_ERROR.value)
                        self.remove_asset_from_in_flight_count()
                        self.run_util.update_metadata_status(guid, self.asset_status_enum.ERROR.value)            
                        return
                except Exception as e:
                    print(e)
                    message = self.run_util.log_exc(self.prefix_id, f"Tried handling has_open_share error for {guid}. Failed to open share in ARS.", e, self.status_enum.CRITICAL_ERROR.value)
                    self.health_caller.error(self.service_name, message, guid, "has_open_share", self.status_enum.CRITICAL_ERROR.value)
                    self.remove_asset_from_in_flight_count()
                    self.run_util.update_metadata_status(guid, self.asset_status_enum.ERROR.value)            
                    return

            # failed to reopen share for transferring to hpc slurm
            if asset_jobs_status == self.status_enum.WAITING.value:

                try:
                    proxy_path, status_code = self.storage_api.open_share(guid, institution, collection, asset_size)
                
                    if proxy_path is not False:

                        self.track_mongo.update_entry(guid, "proxy_path", proxy_path)
                        
                        # create links for all files in the asset
                        files = asset["file_list"]

                        for file in files:
                            if file["deleted"] is not True:
                                name = file["name"]
                                link = proxy_path + name
                                self.track_mongo.update_track_file_list(guid, name, "ars_link", link)

                        self.update_throttle_plus_size(asset)
                        self.track_mongo.update_entry(guid, self.flag_enum.HAS_OPEN_SHARE.value, self.validate_enum.YES.value)
                        message = self.run_util.log_msg(self.prefix_id, f"Successfully handled has_open_share error for {guid}. has_open_share set to {self.validate_enum.YES.value}")
                        self.health_caller.warning(self.service_name, message, guid, self.flag_enum.HAS_OPEN_SHARE.value, self.validate_enum.YES.value)
                        self.run_util.update_metadata_status(guid, self.asset_status_enum.BEING_PROCESSED.value)

                    elif proxy_path is False:                        
                        message = self.run_util.log_msg(self.prefix_id, f"Tried handling has_open_share error for {guid}. Failed to open share in ARS got status {status_code}.", self.status_enum.CRITICAL_ERROR.value)
                        self.health_caller.error(self.service_name, message, guid, self.flag_enum.HAS_OPEN_SHARE.value, self.status_enum.CRITICAL_ERROR.value)
                        self.remove_asset_from_in_flight_count()
                        self.run_util.update_metadata_status(guid, self.asset_status_enum.ERROR.value)            
                        return
                except Exception as e:
                    print(e)
                    message = self.run_util.log_exc(self.prefix_id, f"Tried handling has_open_share error for {guid}. Something else failed.", e, self.status_enum.CRITICAL_ERROR.value)
                    self.health_caller.error(self.service_name, message, guid, self.flag_enum.HAS_OPEN_SHARE.value, self.status_enum.CRITICAL_ERROR.value)
                    self.remove_asset_from_in_flight_count()            
                    self.run_util.update_metadata_status(guid, self.asset_status_enum.ERROR.value)
                    return


        if status == self.erda_enum.METADATA_RECEIVED.value:
            pass

        if status == self.erda_enum.ASSET_RECEIVED.value:
            pass
        
        return
    
    def handle_specify_sync_error(self, asset, guid):

        self.authorization_check()

        ars_status = self.storage_api.get_full_asset_status(guid)

        if ars_status is False:
            entry = self.run_util.log_msg(self.prefix_id, f"Failed getting ARS status for {guid} while handling specify_sync error.")
            self.health_caller.warning(self.service_name, entry)
            return

        error_message = ars_status["data"].error_message
        
        if "SPECIMEN_NOT_FOUND_ERROR" in error_message:

            metadata = self.metadata_mongo.get_entry("_id", guid)

            # TODO implement specify api calls to check for specimen existence
            specimens = metadata["barcode"]

            try:
                closed = self.storage_api.close_share(guid)
            except Exception as e:
                entry = self.run_util.log_exc(self.prefix_id, f"Failed to close file proxy share for {guid} while handling specify_sync error for SPECIMEN_NOT_FOUND_ERROR. One or more of the specimen(s) {specimens} not found in Specify. specify_sync is upgraded to CRITICAL_ERROR and available_for_services set to NO. The file proxy share will remain open until action is taken.", e, self.status_enum.CRITICAL_ERROR.value)
                self.health_caller.warning(self.service_name, entry, guid, self.flag_enum.SPECIFY_SYNC.value, self.status_enum.CRITICAL_ERROR.value)
                self.track_mongo.update_entry(guid, self.flag_enum.AVAILABLE_FOR_SERVICES.value, self.validate_enum.NO.value)
                self.track_mongo.update_entry(guid, self.flag_enum.SPECIFY_SYNC.value, self.validate_enum.CRITICAL_ERROR.value)
                self.remove_asset_from_in_flight_count()
                self.run_util.update_metadata_status(guid, self.asset_status_enum.ERROR.value)
                return

            if closed is True:
                self.track_mongo.update_entry(guid, "has_open_share", self.validate_enum.NO.value)
            else:
                entry = self.run_util.log_msg(self.prefix_id, f"Failed to close file proxy share for {guid} while handling specify_sync error for SPECIMEN_NOT_FOUND_ERROR. One or more of the specimen(s) {specimens} not found in Specify. specify_sync is upgraded to CRITICAL_ERROR and available_for_services set to NO. The file proxy share will remain open until action is taken.", self.status_enum.CRITICAL_ERROR.value)
                self.health_caller.warning(self.service_name, entry, guid, self.flag_enum.SPECIFY_SYNC.value, self.status_enum.CRITICAL_ERROR.value)
                self.track_mongo.update_entry(guid, self.flag_enum.AVAILABLE_FOR_SERVICES.value, self.validate_enum.NO.value)
                self.track_mongo.update_entry(guid, self.flag_enum.SPECIFY_SYNC.value, self.validate_enum.CRITICAL_ERROR.value)
                self.run_util.update_metadata_status(guid, self.asset_status_enum.ERROR.value)
                self.remove_asset_from_in_flight_count()
                return

            self.track_mongo.update_entry(guid, self.flag_enum.SPECIFY_SYNC.value, self.status_enum.CRITICAL_ERROR.value)
            self.track_mongo.update_entry(guid, self.flag_enum.AVAILABLE_FOR_SERVICES.value, self.validate_enum.NO.value)
            
            entry = self.run_util.log_msg(self.prefix_id, f"{guid} failed to sync with specify in ARS. One or more of the specimen(s) {specimens} not found in Specify. Fileproxy share has been deleted and the asset removed throttle procedures. Asset file is still in ERDA and metadata in ARS. Will set specify_sync to CRITICAL_ERROR, has_open_share to NO and available_for_services to NO.")
            self.health_caller.error(self.service_name, entry, guid, self.flag_enum.SPECIFY_SYNC.value , self.status_enum.CRITICAL_ERROR.value)
            self.run_util.update_metadata_status(guid, self.asset_status_enum.ERROR.value)
            self.remove_asset_from_in_flight_count()
            return
        """
        # TODO add a temp variable to track data and have validate sync specify remove this - implement checks for it here to avoid looping the same errored asset
        # TODO needs access to the direct sync with specify endpoint, cant resync without getting rid of the error by doing a fake update to the metadata
        if "UNKNOWN_ERROR" in error_message:
            
            metadata = self.metadata_mongo.get_entry("_id", guid)

            if asset["asset_size"] == ars_status["data"].share_allocation_mb:

                files = self.storage_api.get_files_available(guid, metadata["institution"], metadata["collection"])
                if files is not False:
                    self.track_mongo.update_entry(guid, self.flag_enum.SPECIFY_SYNC.value, self.validate_enum.PREPARE.value)
                    entry = self.run_util.log_msg(self.prefix_id, f"Handled specify_sync error for {guid} with UNKNOWN_ERROR in status message from ARS. Asset had share allocation match asset size. Asset files were found to be available in ARS. specify_sync set to {self.validate_enum.PREPARE.value} and should return to normal flow.")
                    self.health_caller.warning(self.service_name, entry, guid, self.flag_enum.SPECIFY_SYNC.value, self.validate_enum.PREPARE.value)
                    return
        """
        # others
        self.track_mongo.update_entry(guid, self.flag_enum.SPECIFY_SYNC.value, self.status_enum.CRITICAL_ERROR.value)
        self.track_mongo.update_entry(guid, self.flag_enum.AVAILABLE_FOR_SERVICES.value, self.validate_enum.NO.value)
        entry = self.run_util.log_msg(self.prefix_id, f"Tried handling specify_sync error for {guid}. Could not determine the issue. Will need manual handling. specify_sync set to {self.status_enum.CRITICAL_ERROR.value}")
        self.health_caller.error(self.service_name, entry, guid, self.flag_enum.SPECIFY_SYNC.value, self.status_enum.CRITICAL_ERROR.value)
        self.run_util.update_metadata_status(guid, self.asset_status_enum.ERROR.value)            
        return

    def update_throttle_plus_size(self, asset):
        self.throttle_mongo.add_to_amount("total_asset_size_mb", "value", asset["asset_size"])
        self.throttle_mongo.add_to_amount("total_reopened_share_size_mb", "value", asset["asset_size"])
        # TODO decide if this belongs here. But seems natural enough to include it. 
        self.track_mongo.update_entry(asset["_id"], "temporary_reopened_share_status", True)

    def remove_asset_from_in_flight_count(self):
        self.throttle_mongo.subtract_one_from_count("assets_in_flight", "value")

if __name__ == '__main__':
    AssetErrorStatusHandler()