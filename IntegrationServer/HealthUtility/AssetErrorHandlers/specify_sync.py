import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from HealthUtility.AssetErrorHandlers.a_base_error_handler import BaseErrorHandler

class SpecifySyncErrorHandler(BaseErrorHandler):

        def __init__(self, context):
            super().__init__(context)

        def handle_specify_sync_error(self, asset):

            guid = asset["_id"]
            
            self.ctx.authorization_check()

            ars_status = self.ctx.storage_api.get_full_asset_status(guid)

            if ars_status is False:
                entry = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Failed getting ARS status for {guid} while handling specify_sync error.")
                self.ctx.health_caller.warning(self.ctx.service_name, entry)
                return

            error_message = ars_status["data"].error_message

            if error_message is not None:        
            
                if "SPECIMEN_NOT_FOUND_ERROR" in error_message:

                    metadata = self.ctx.metadata_mongo.get_entry("_id", guid)

                    # TODO implement specify api calls to check for specimen existence
                    specimens = metadata["barcode"]

                    try:
                        closed = self.ctx.storage_api.close_share(guid)
                    except Exception as e:
                        self.failure_to_handle_updates(guid)
                        entry = self.ctx.run_util.log_exc(self.ctx.prefix_id, f"Failed to close file proxy share for {guid} while handling specify_sync error for SPECIMEN_NOT_FOUND_ERROR. One or more of the specimen(s) {specimens} not found in Specify. specify_sync is upgraded to CRITICAL_ERROR and available_for_services set to NO. The file proxy share will remain open until action is taken.", e, self.ctx.status_enum.CRITICAL_ERROR.value)
                        self.ctx.health_caller.warning(self.ctx.service_name, entry, guid, self.ctx.flag_enum.SPECIFY_SYNC.value, self.ctx.status_enum.CRITICAL_ERROR.value)
                        return

                    if closed is True:
                        self.ctx.track_mongo.update_entry(guid, "has_open_share", self.ctx.validate_enum.NO.value)
                    else:
                        self.failure_to_handle_updates(guid)
                        entry = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Failed to close file proxy share for {guid} while handling specify_sync error for SPECIMEN_NOT_FOUND_ERROR. One or more of the specimen(s) {specimens} not found in Specify. specify_sync is upgraded to CRITICAL_ERROR and available_for_services set to NO. The file proxy share will remain open until action is taken.", self.ctx.status_enum.CRITICAL_ERROR.value)
                        self.ctx.health_caller.warning(self.ctx.service_name, entry, guid, self.ctx.flag_enum.SPECIFY_SYNC.value, self.ctx.status_enum.CRITICAL_ERROR.value)
                        return

                    self.failure_to_handle_updates(guid)
                    entry = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"{guid} failed to sync with specify in ARS. One or more of the specimen(s) {specimens} not found in Specify. Fileproxy share has been deleted and the asset removed throttle procedures. Asset file is still in ERDA and metadata in ARS. Will set specify_sync to CRITICAL_ERROR, has_open_share to NO and available_for_services to NO.")
                    self.ctx.health_caller.error(self.ctx.service_name, entry, guid, self.ctx.flag_enum.SPECIFY_SYNC.value , self.ctx.status_enum.CRITICAL_ERROR.value)
                    return
                
                if "FILE_DOWNLOAD_ERROR" in error_message:

                    # TODO check if file is in ARS and ERDA
                    # Try download check crc
                    # delete download
                    # reset sync options if everything is ok or retry sync?

                    # fail to handle try close share   
                    try:
                        closed = self.ctx.storage_api.close_share(guid)
                    except Exception as e:
                        self.failure_to_handle_updates(guid)
                        entry = self.ctx.run_util.log_exc(self.ctx.prefix_id, f"Failed to close file proxy share for {guid} while handling specify_sync error for FILE_DOWNLOAD_ERROR. Specify_sync is upgraded to CRITICAL_ERROR and available_for_services set to NO. The file proxy share will remain open until action is taken.", e, self.ctx.status_enum.CRITICAL_ERROR.value)
                        self.ctx.health_caller.warning(self.ctx.service_name, entry, guid, self.ctx.flag_enum.SPECIFY_SYNC.value, self.ctx.status_enum.CRITICAL_ERROR.value)
                        return

                    if closed is True:
                        self.ctx.track_mongo.update_entry(guid, "has_open_share", self.ctx.validate_enum.NO.value)
                    else:
                        self.failure_to_handle_updates(guid)
                        entry = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Failed to close file proxy share for {guid} while handling specify_sync error for FILE_DOWNLOAD_ERROR. Specify_sync is upgraded to CRITICAL_ERROR and available_for_services set to NO. The file proxy share will remain open until action is taken.", self.ctx.status_enum.CRITICAL_ERROR.value)
                        self.ctx.health_caller.warning(self.ctx.service_name, entry, guid, self.ctx.flag_enum.SPECIFY_SYNC.value, self.ctx.status_enum.CRITICAL_ERROR.value)
                        return

                    # end fail to handle
                    self.failure_to_handle_updates(guid)
                    entry = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"{guid} failed to sync with specify from ARS. Due to FILE_DOWNLOAD_ERROR. Fileproxy share has been deleted and the asset removed throttle procedures. Will set specify_sync to CRITICAL_ERROR, has_open_share to NO and available_for_services to NO.")
                    self.ctx.health_caller.error(self.ctx.service_name, entry, guid, self.ctx.flag_enum.SPECIFY_SYNC.value , self.ctx.status_enum.CRITICAL_ERROR.value)
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
            self.failure_to_handle_updates(guid)
            entry = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Tried handling specify_sync error for {guid}. Could not determine the issue. Will need manual handling. specify_sync set to {self.ctx.status_enum.CRITICAL_ERROR.value}. If any ARS error message: {error_message}")
            self.ctx.health_caller.error(self.ctx.service_name, entry, guid, self.ctx.flag_enum.SPECIFY_SYNC.value, self.ctx.status_enum.CRITICAL_ERROR.value)                       
            return
        
        def failure_to_handle_updates(self, guid):
            self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.AVAILABLE_FOR_SERVICES.value, self.ctx.validate_enum.NO.value)
            self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.SPECIFY_SYNC.value, self.ctx.validate_enum.CRITICAL_ERROR.value)
            self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.ERROR.value)
            self.util.remove_asset_from_in_flight_count()
            self.util.remove_asset_from_await_specify_sync_count()
            