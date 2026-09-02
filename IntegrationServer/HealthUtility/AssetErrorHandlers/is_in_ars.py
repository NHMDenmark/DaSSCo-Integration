import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '../..'))
sys.path.append(project_root)

from HealthUtility.AssetErrorHandlers.a_base_error_handler import BaseErrorHandler

class IsInArsErrorHandler(BaseErrorHandler):

        def __init__(self, context):
            super().__init__(context)

        def handle_is_in_ars_error(self, asset):
              
            guid = asset["_id"]
            allocation_size = asset["asset_size"]

            if allocation_size == -1:
                # FAIL
                pass 

            self.ctx.authorization_check()

            ars_status = self.ctx.storage_api.get_full_asset_status(guid)

            if ars_status is False:

                update_metadata_status = asset[self.ctx.flag_enum.UPDATE_METADATA.value]
                if update_metadata_status == self.ctx.validate_enum.ERROR.value:
                    self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.UPDATE_METADATA.value, self.ctx.validate_enum.NO.value)

                metadata_status = self.ctx.metadata_mongo.get_value_for_key(guid, "status")
                if metadata_status == self.ctx.asset_status_enum.PROCESSING_ISSUE.value:
                     self.ctx.metadata_mongo.update_entry(guid, "status", self.ctx.asset_status_enum.BEING_PROCESSED.value)
                
                created, response, exc, status_code = self.ctx.storage_api.create_asset(guid, allocation_size)
                #print(created, response, exc, status_code)

                if created is True:

                    ars_status = self.ctx.storage_api.get_full_asset_status(guid)
                    
                    if ars_status["data"].share_allocation_mb == allocation_size:
                        # success
                        open_type = self.util.determine_asset_open_share_type(asset)
                        if open_type == "new":
                             self.util.update_throttle_new_plus_size(asset)

                        if open_type == "derivative":
                             self.util.update_throttle_derivative_plus_size(asset)

                        self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.IS_IN_ARS.value, self.ctx.validate_enum.YES.value)
                        self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.HAS_OPEN_SHARE.value, self.ctx.validate_enum.YES.value)
                        self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.HAS_NEW_FILE.value, self.ctx.validate_enum.YES.value)        

                        message = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Successfully handled is_in_ars error for {guid}. Asset was first not found in ARS. Created the asset in ARS with share allocation matching asset size. Metadata status reset to BEING_PROCESSED. is_in_ars, has_new_file and has_open_share set to YES.")
                        self.ctx.health_caller.warning(self.ctx.service_name, message, guid, "is_in_ars", self.ctx.validate_enum.YES.value)

                        return
                    else:
                        pass

                if created is False:
                     pass
                
                return

            elif ars_status["data"].status == [self.ctx.erda_enum.METADATA_RECEIVED.value]:
                 
                if ars_status["data"].share_allocation_mb == asset["asset_size"]:
                    
                    self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.IS_IN_ARS.value, self.ctx.validate_enum.YES.value)
                    self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.HAS_OPEN_SHARE.value, self.ctx.validate_enum.YES.value)
                    open_type = self.util.determine_asset_open_share_type(asset)
                    if open_type == "new":
                        self.util.update_throttle_new_plus_size(asset)                    
                    if open_type == "derivative":
                        self.util.update_throttle_derivative_plus_size(asset)
                    message = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Successfully handled is_in_ars error for {guid}. Asset found to be in ARS with share allocation matching asset size. is_in_ars and has_open_share set to {self.ctx.validate_enum.YES.value}")
                    self.ctx.health_caller.warning(self.ctx.service_name, message, guid, "is_in_ars", self.ctx.validate_enum.YES.value)
                    self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.BEING_PROCESSED.value)
                    return

            else:
                 print(f"Could not handle: {guid}")        
