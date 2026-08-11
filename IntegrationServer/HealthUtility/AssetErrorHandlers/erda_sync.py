import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '../..'))
sys.path.append(project_root)

import time
from HealthUtility.AssetErrorHandlers.a_base_error_handler import BaseErrorHandler

class ErdaSyncErrorHandler(BaseErrorHandler):

        def __init__(self, context):
            super().__init__(context)

        def handle_erda_sync_error(self, asset):
            
            guid = asset["_id"]

            self.ctx.authorization_check()

            ars_status = self.ctx.storage_api.get_full_asset_status(guid)

            # gives time for ARS to update - in case this is about the share still appearing open despite sync completed
            time.sleep(120)

            if ars_status["data"].status == self.ctx.erda_enum.COMPLETED.value and ars_status["data"].share_allocation_mb is None:
                
                self.ctx.throttle_mongo.add_one_to_count("await_sync_asset_count", "value")
                self.ctx.track_mongo.update_entry(guid, self.ctx.flag_enum.ERDA_SYNC.value, self.ctx.validate_enum.AWAIT.value)
                print(f"found {guid} to have been successfully synced to erda - sent asset back to normal flow")
                self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.BEING_PROCESSED.value)

            else:
                print(f"unable to handle {guid} - set to critical error")
                message = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Tried handling erda_sync error for {guid}. Could not determine the issue. Will need manual handling. erda_sync set to {self.ctx.status_enum.CRITICAL_ERROR.value}")
                self.ctx.health_caller.error(self.ctx.service_name, message, guid, "erda_sync", self.ctx.status_enum.CRITICAL_ERROR.value)
                self.util.remove_asset_from_in_flight_count()
                self.ctx.run_util.update_metadata_status(guid, self.ctx.asset_status_enum.ERROR.value)