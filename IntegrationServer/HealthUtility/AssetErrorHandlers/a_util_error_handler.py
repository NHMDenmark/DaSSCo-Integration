import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from HealthUtility.AssetErrorHandlers.a_service_context import ServiceContext

class UtilErrorHandler:

    def __init__(self, context: ServiceContext):
        self.ctx = context

    def update_throttle_reopen_plus_size(self, asset):
        self.ctx.throttle_mongo.add_to_amount("total_asset_size_mb", "value", asset["asset_size"])
        self.ctx.throttle_mongo.add_to_amount("total_reopened_share_size_mb", "value", asset["asset_size"])
        # TODO decide if this belongs here. But seems natural enough to include it. 
        self.ctx.track_mongo.update_entry(asset["_id"], "temporary_reopened_share_status", True)

    def update_throttle_new_plus_size(self, asset):
        self.ctx.throttle_mongo.add_to_amount("total_asset_size_mb", "value", asset["asset_size"])
        self.ctx.throttle_mongo.add_to_amount("total_new_asset_size_mb", "value", asset["asset_size"])

    def update_throttle_derivative_plus_size(self, asset):
        self.ctx.throttle_mongo.add_to_amount("total_asset_size_mb", "value", asset["asset_size"])
        self.ctx.throttle_mongo.add_to_amount("total_derivative_size_mb", "value", asset["asset_size"])

    def remove_asset_from_in_flight_count(self):
        self.ctx.throttle_mongo.subtract_one_from_count("assets_in_flight", "value")

    def subtract_asset_size_from_throttle(self, asset, share_style):

        if share_style in ["reopened", "new", "derivative"]:

            self.ctx.throttle_mongo.subtract_from_amount("total_asset_size_mb", "value", asset["asset_size"])

            if share_style == "reopened":
                self.ctx.throttle_mongo.subtract_from_amount("total_reopened_share_size_mb", "value", asset["asset_size"])
                self.ctx.throttle_mongo.delete_field(asset["_id"], "temporary_reopened_share_status")
            if share_style == "new":
                self.ctx.throttle_mongo.subtract_from_amount("total_new_asset_size_mb", "value", asset["asset_size"])
            if share_style == "derivative":
                self.ctx.throttle_mongo.subtract_from_amount("total_derivative_size_mb", "value", asset["asset_size"])

        else:
            self.ctx.throttle_mongo.subtract_from_amount("total_asset_size_mb", "value", asset["asset_size"])

    def close_proxy_share(self, guid):
        try:
            closed = self.ctx.storage_api.close_share(guid)
            
            if closed is not True:
                entry = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"Failed to close file proxy share for {guid} while handling error status.")
                self.ctx.health_caller.error(self.ctx.service_name, entry, guid)
                raise Exception("Failed to close proxy share")

        except Exception as e:
            raise e
        
    def remove_asset_from_await_specify_sync_count(self):
        self.ctx.throttle_mongo.subtract_one_from_count("await_specify_sync_count", "value")
        