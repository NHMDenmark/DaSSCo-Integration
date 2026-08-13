import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '../..'))
sys.path.append(project_root)

from HealthUtility.AssetErrorHandlers.a_base_error_handler import BaseErrorHandler

class HasNewFileErrorHandler(BaseErrorHandler):

        def __init__(self, context):
            super().__init__(context)

        def handle_has_new_file_error(self, asset):

            guid = asset["_id"]

            self.ctx.authorization_check()

            ars_status = self.ctx.storage_api.get_full_asset_status(guid)

            if ars_status is False:
                entry = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Failed getting ARS status for {guid} while handling has_new_file error.")
                self.ctx.health_caller.warning(self.ctx.service_name, entry)
                return

            status = ars_status["data"].status
            ars_share_allocation = ars_status["data"].share_allocation_mb
            error_message = ars_status["data"].error_message
            
            asset_size = asset["asset_size"]

            institution = self.ctx.metadata_mongo.get_value_for_key(guid, "institution")
            collection = self.ctx.metadata_mongo.get_value_for_key(guid, "collection")

            share_type = None
            if ars_share_allocation is not None:
                share_type = self.util.determine_asset_open_share_type(asset)

            if error_message is not None:
                pass
            else:
                pass
            
            if ars_share_allocation is None:

                try:
                    proxy_path, open_status = self.ctx.storage_api.open_share(guid, institution, collection, asset_size)

                    if proxy_path is not False:

                        self.ctx.track_mongo.update_entry(guid, "proxy_path", proxy_path)
                        
                        # create links for all files in the asset
                        files = asset["file_list"]

                        for file in files:
                            if file["deleted"] is not True:
                                name = file["name"]
                                link = proxy_path + name
                                self.ctx.track_mongo.update_track_file_list(guid, name, "ars_link", link)
                        self.util.update_throttle_new_plus_size(asset)
                        self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.HAS_NEW_FILE.value, self.ctx.validate_enum.YES.value)
                        entry = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Found file proxy share to not exist for {guid}. Opened a new file share in ARS. has_new_file set to {self.ctx.validate_enum.YES.value}")
                        self.ctx.health_caller.warning(self.ctx.service_name, entry, guid, self.ctx.flag_enum.HAS_NEW_FILE.value, self.ctx.validate_enum.YES.value)
                        self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.BEING_PROCESSED.value)
                        return
                    
                    elif proxy_path is False:                        
                        entry = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Found file proxy share to not exist for {guid} while handling has_new_file error. Failed to open share in ARS.", self.ctx.status_enum.CRITICAL_ERROR.value)
                        self.ctx.health_caller.error(self.ctx.service_name, entry, guid, self.ctx.flag_enum.HAS_NEW_FILE.value, self.ctx.status_enum.CRITICAL_ERROR.value)
                        self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.HAS_NEW_FILE.value, self.ctx.status_enum.CRITICAL_ERROR.value)
                        self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.ERROR.value)            
                        self.util.remove_asset_from_in_flight_count()
                        try:
                            self.util.close_proxy_share(guid)
                            self.util.subtract_asset_size_from_throttle(asset, share_type)
                        except Exception as e:
                            entry = self.ctx.run_util.log_exc(self.ctx.prefix_id, f"Also failed to close file proxy share for {guid} while handling has_new_file error.", e, self.ctx.status_enum.CRITICAL_ERROR.value)
                            self.ctx.health_caller.error(self.ctx.service_name, entry, guid)
                        return

                except Exception as e:
                    entry = self.ctx.run_util.log_exc(self.ctx.prefix_id, f"Failed to open file proxy share for {guid} while handling has_new_file error. has_new_file is upgraded to CRITICAL_ERROR and available_for_services set to NO.", e, self.ctx.status_enum.CRITICAL_ERROR.value)
                    self.ctx.health_caller.error(self.ctx.service_name, entry, guid, self.ctx.flag_enum.HAS_NEW_FILE.value, self.ctx.status_enum.CRITICAL_ERROR.value)
                    self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.HAS_NEW_FILE.value, self.ctx.status_enum.CRITICAL_ERROR.value)
                    self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.AVAILABLE_FOR_SERVICES.value, self.ctx.validate_enum.NO.value)
                    self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.ERROR.value)
                    self.util.remove_asset_from_in_flight_count()
                    try:
                        self.util.close_proxy_share(guid)
                        self.util.subtract_asset_size_from_throttle(asset, share_type)
                    except Exception as e:
                        entry = self.ctx.run_util.log_exc(self.ctx.prefix_id, f"Also failed to close file proxy share for {guid} while handling has_new_file error.", e, self.ctx.status_enum.CRITICAL_ERROR.value)
                        self.ctx.health_caller.error(self.ctx.service_name, entry, guid)
                    return

            if asset_size > ars_share_allocation:
                
                try:
                    changed, status, note = self.ctx.storage_api.change_share_allocation(guid, asset_size)

                    if changed is True:
                        self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.HAS_NEW_FILE.value, self.ctx.validate_enum.YES.value)
                        entry = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Updated share allocation in ARS for {guid} while handling has_new_file error. has_new_file set to {self.ctx.validate_enum.YES.value}")
                        self.ctx.health_caller.warning(self.ctx.service_name, entry, guid, self.ctx.flag_enum.HAS_NEW_FILE.value, self.ctx.validate_enum.YES.value)
                        self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.BEING_PROCESSED.value)
                        return
                    else:
                        entry = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Tried updating share allocation in ARS for {guid} while handling has_new_file error but failed. Share allocation status: {status}. note: {note}. Share will be closed.")
                        self.ctx.health_caller.error(self.ctx.service_name, entry, guid, self.ctx.flag_enum.HAS_NEW_FILE.value, self.ctx.status_enum.CRITICAL_ERROR.value)
                        self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.HAS_NEW_FILE.value, self.ctx.status_enum.CRITICAL_ERROR.value)
                        self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.AVAILABLE_FOR_SERVICES.value, self.ctx.validate_enum.NO.value)
                        self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.ERROR.value)
                        self.util.remove_asset_from_in_flight_count()
                        try:
                            self.util.close_proxy_share(guid)
                            self.util.subtract_asset_size_from_throttle(asset, share_type)
                        except Exception as e:
                            entry = self.ctx.run_util.log_exc(self.ctx.prefix_id, f"Also failed to close file proxy share for {guid} while handling has_new_file error.", e, self.ctx.status_enum.CRITICAL_ERROR.value)
                            self.ctx.health_caller.error(self.ctx.service_name, entry, guid)            
                        return
                except Exception as e:
                    entry = self.ctx.run_util.log_exc(self.ctx.prefix_id, f"Failed updating share allocation in ARS for {guid} while handling has_new_file error. has_new_file is upgraded to CRITICAL_ERROR, share will be closed and available_for_services set to NO. ", e, self.ctx.status_enum.CRITICAL_ERROR.value)
                    self.ctx.health_caller.error(self.ctx.service_name, entry, guid, self.ctx.flag_enum.HAS_NEW_FILE.value, self.ctx.status_enum.CRITICAL_ERROR.value)
                    self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.HAS_NEW_FILE.value, self.ctx.status_enum.CRITICAL_ERROR.value)
                    self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.AVAILABLE_FOR_SERVICES.value, self.ctx.validate_enum.NO.value)
                    self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.ERROR.value)
                    self.util.remove_asset_from_in_flight_count()
                    try:
                        self.util.close_proxy_share(guid)
                        self.util.subtract_asset_size_from_throttle(asset, share_type)
                    except Exception as e:
                        entry = self.ctx.run_util.log_exc(self.ctx.prefix_id, f"Also failed to close file proxy share for {guid} while handling has_new_file error.", e, self.ctx.status_enum.CRITICAL_ERROR.value)
                        self.ctx.health_caller.error(self.ctx.service_name, entry, guid)            
                    return

            # others
            self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.HAS_NEW_FILE.value, self.ctx.status_enum.CRITICAL_ERROR.value)
            entry = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Tried handling has_new_file error for {guid}. Could not determine the issue. Will need manual handling. has_new_file set to {self.ctx.status_enum.CRITICAL_ERROR.value}. ARS error message: {error_message}")
            self.ctx.health_caller.error(self.ctx.service_name, entry, guid, self.ctx.flag_enum.HAS_NEW_FILE.value, self.ctx.status_enum.CRITICAL_ERROR.value)
            self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.ERROR.value)
            self.util.remove_asset_from_in_flight_count()
            try:
                self.util.close_proxy_share(guid)
                self.util.subtract_asset_size_from_throttle(asset, share_type)
            except Exception as e:
                entry = self.ctx.run_util.log_exc(self.ctx.prefix_id, f"Also failed to close file proxy share for {guid} while handling has_new_file error.", e, self.ctx.status_enum.CRITICAL_ERROR.value)
                self.ctx.health_caller.error(self.ctx.service_name, entry, guid)            
            return            