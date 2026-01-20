import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from IntegrationServer.HealthUtility.TrackFlagErrorHandlers.a_base_error_handler import BaseErrorHandler

class HasOpenShareErrorHandler(BaseErrorHandler):

        def __init__(self, context):
            super().__init__(context)

        def handle_has_open_share_error(self, asset, guid):
        
            self.ctx.authorization_check()

            ars_status = self.ctx.storage_api.get_full_asset_status(guid)

            if ars_status is False:
                print(f"unable to handle {guid} - set to critical error")
                self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.HAS_OPEN_SHARE.value, self.ctx.status_enum.CRITICAL_ERROR.value)
                message = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Tried handling has_open_share error for {guid}. Could not determine the issue. Failed to get information about asset from ARS. has_open_share set to {self.ctx.status_enum.CRITICAL_ERROR.value}")
                self.ctx.health_caller.error(self.ctx.service_name, message, guid, "has_open_share", self.ctx.status_enum.CRITICAL_ERROR.value)
                self.util.remove_asset_from_in_flight_count()
                self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.ERROR.value)            
                return
            
            status = ars_status["data"].status
            share_allocation = ars_status["data"].share_allocation_mb
            error_message = ars_status["data"].error_message
            asset_available = asset[self.ctx.flag_enum.AVAILABLE_FOR_SERVICES.value]
            asset_erda_sync = asset[self.ctx.flag_enum.ERDA_SYNC.value]
            asset_size = asset["asset_size"]
            asset_jobs_status = asset["jobs_status"]
            asset_specify_sync = asset[self.ctx.flag_enum.SPECIFY_SYNC.value]
            institution = self.ctx.metadata_mongo.get_value_for_key(guid, "institution")
            collection = self.ctx.metadata_mongo.get_value_for_key(guid, "collection")

            # asset share was opened despite the status being sent back saying otherwise
            if share_allocation is not None and share_allocation == asset_size:
                        # asset has files available and share allocation exists - should be fine to move on
                        files = self.ctx.storage_api.get_files_available(guid, institution, collection)
                        if files is not False:
                            self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.HAS_OPEN_SHARE.value, self.ctx.validate_enum.YES.value)
                            message = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Successfully handled has_open_share error for {guid}. Asset had share allocation match asset size. Asset files were found to be available in ARS. has_open_share set to {self.ctx.validate_enum.YES.value}")
                            self.ctx.health_caller.warning(self.ctx.service_name, message, guid, "has_open_share", self.ctx.validate_enum.YES.value)
                            self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.BEING_PROCESSED.value)
                            return

            if status == self.ctx.erda_enum.ERDA_SYNCHRONISED.value:

                # specify open share fails -> retry opening the share
                if asset_specify_sync == self.ctx.validate_enum.PREPARE.value:
                    
                    try:
                        proxy_path, status_code = self.ctx.storage_api.open_share(guid, institution, collection, asset_size)
                    
                        if proxy_path is not False:

                            self.ctx.track_mongo.update_entry(guid, "proxy_path", proxy_path)
                            
                            # create links for all files in the asset
                            files = asset["file_list"]

                            for file in files:
                                if file["deleted"] is not True:
                                    name = file["name"]
                                    link = proxy_path + name
                                    self.ctx.track_mongo.update_track_file_list(guid, name, "ars_link", link)

                            self.ctx.update_throttle_plus_size(asset)
                            self.ctx.track_mongo.update_entry(guid, "has_open_share", self.ctx.validate_enum.YES.value)
                            message = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Successfully handled has_open_share error for {guid}. has_open_share set to {self.ctx.validate_enum.YES.value}")
                            self.ctx.health_caller.warning(self.ctx.service_name, message, guid, "has_open_share", self.ctx.validate_enum.YES.value)
                            self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.BEING_PROCESSED.value)

                        elif proxy_path is False:                        
                            message = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Tried handling has_open_share error for {guid}. Failed to open share in ARS.", self.ctx.status_enum.CRITICAL_ERROR.value)
                            self.ctx.health_caller.warning(self.ctx.service_name, message, guid, "has_open_share", self.ctx.status_enum.CRITICAL_ERROR.value)
                            self.util.remove_asset_from_in_flight_count()
                            self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.ERROR.value)            
                            return
                    except Exception as e:
                        print(e)
                        message = self.ctx.run_util.log_exc(self.ctx.prefix_id, f"Tried handling has_open_share error for {guid}. Failed to open share in ARS.", e, self.ctx.status_enum.CRITICAL_ERROR.value)
                        self.ctx.health_caller.error(self.ctx.service_name, message, guid, "has_open_share", self.ctx.status_enum.CRITICAL_ERROR.value)
                        self.util.remove_asset_from_in_flight_count()
                        self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.ERROR.value)            
                        return

                # failed to reopen share for transferring to hpc slurm
                if asset_jobs_status == self.ctx.status_enum.WAITING.value:
                    try:
                        proxy_path, status_code = self.ctx.storage_api.open_share(guid, institution, collection, asset_size)
                    
                        if proxy_path is not False:

                            self.ctx.track_mongo.update_entry(guid, "proxy_path", proxy_path)
                            
                            # create links for all files in the asset
                            files = asset["file_list"]

                            for file in files:
                                if file["deleted"] is not True:
                                    name = file["name"]
                                    link = proxy_path + name
                                    self.ctx.track_mongo.update_track_file_list(guid, name, "ars_link", link)

                            self.util.update_throttle_plus_size(asset)
                            self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.HAS_OPEN_SHARE.value, self.ctx.validate_enum.YES.value)
                            message = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Successfully handled has_open_share error for {guid}. has_open_share set to {self.ctx.validate_enum.YES.value}")
                            self.ctx.health_caller.warning(self.ctx.service_name, message, guid, self.ctx.flag_enum.HAS_OPEN_SHARE.value, self.ctx.validate_enum.YES.value)
                            self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.BEING_PROCESSED.value)

                        elif proxy_path is False:                        
                            message = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Tried handling has_open_share error for {guid}. Failed to open share in ARS got status {status_code}.", self.ctx.status_enum.CRITICAL_ERROR.value)
                            self.ctx.health_caller.error(self.ctx.service_name, message, guid, self.ctx.flag_enum.HAS_OPEN_SHARE.value, self.ctx.status_enum.CRITICAL_ERROR.value)
                            self.util.remove_asset_from_in_flight_count()
                            self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.ERROR.value)            
                            return
                    except Exception as e:
                        print(e)
                        message = self.ctx.run_util.log_exc(self.ctx.prefix_id, f"Tried handling has_open_share error for {guid}. Something else failed.", e, self.ctx.status_enum.CRITICAL_ERROR.value)
                        self.ctx.health_caller.error(self.ctx.service_name, message, guid, self.ctx.flag_enum.HAS_OPEN_SHARE.value, self.ctx.status_enum.CRITICAL_ERROR.value)
                        self.util.remove_asset_from_in_flight_count()            
                        self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.ERROR.value)
                        return


            if status == self.ctx.erda_enum.METADATA_RECEIVED.value:
                pass

            if status == self.ctx.erda_enum.ASSET_RECEIVED.value:
                pass
            
            return