import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from HealthUtility.AssetErrorHandlers.a_base_error_handler import BaseErrorHandler

class IsInArsErrorHandler(BaseErrorHandler):

        def __init__(self, context):
            super().__init__(context)

        def handle_is_in_ars_error(self, asset):
              
            guid = asset["_id"] 

            self.ctx.authorization_check()

            ars_status = self.ctx.storage_api.get_full_asset_status(guid)

            if ars_status is False:

                pass

            elif ars_status["data"].status == [self.ctx.erda_enum.METADATA_RECEIVED.value]:
                 
                if ars_status["data"].share_allocation_mb == asset["asset_size"]:
                    
                    self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.IS_IN_ARS.value, self.ctx.validate_enum.YES.value)
                    self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.HAS_OPEN_SHARE.value, self.ctx.validate_enum.YES.value)
                    self.util.update_throttle_new_plus_size(asset)
                    message = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Successfully handled is_in_ars error for {guid}. Asset found to be in ARS with share allocation matching asset size. is_in_ars and has_open_share set to {self.ctx.validate_enum.YES.value}")
                    self.ctx.health_caller.warning(self.ctx.service_name, message, guid, "is_in_ars", self.ctx.validate_enum.YES.value)
                    self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.BEING_PROCESSED.value)
                    return
                    
