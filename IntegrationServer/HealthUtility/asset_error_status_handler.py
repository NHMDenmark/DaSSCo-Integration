import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from HealthUtility.TrackFlagErrorHandlers.a_service_context import ServiceContext
from HealthUtility.TrackFlagErrorHandlers.has_new_file import HasNewFileErrorHandler
from HealthUtility.TrackFlagErrorHandlers.has_open_share import HasOpenShareErrorHandler
from HealthUtility.TrackFlagErrorHandlers.erda_sync import ErdaSyncErrorHandler
from HealthUtility.TrackFlagErrorHandlers.specify_sync import SpecifySyncErrorHandler

"""
# TODO Description. Add in flight throttle count
"""
class AssetErrorStatusHandler():

    def __init__(self):

        self.ctx = ServiceContext()

        self.has_new_file_handler = HasNewFileErrorHandler(self.ctx)
        self.has_open_share_handler = HasOpenShareErrorHandler(self.ctx)
        self.erda_sync_handler = ErdaSyncErrorHandler(self.ctx)
        self.specify_sync_handler = SpecifySyncErrorHandler(self.ctx)

        self.ctx.run_util.service_starting_updates()

        entry = self.ctx.run_util.log_msg(self.ctx.prefix_id, f"{self.ctx.service_name} status changed at initialisation to {self.ctx.status_enum.RUNNING.value}")
        self.ctx.health_caller.run_status_change(self.ctx.service_name, self.ctx.status_enum.RUNNING.value, entry)
        
        try:
            self.loop()
        except Exception as e:
            print("service crashed", e)
            try:
                entry = self.ctx.run_util.log_exc(self.ctx.prefix_id, f"{self.ctx.service_name} crashed.", e, self.ctx.status_enum.CRITICAL_ERROR.value)
                self.ctx.health_caller.unexpected_error(self.ctx.service_name, entry)
            except:
                print(f"failed to inform about crash")
            self.ctx.run_util.service_stopping_updates()
            self.ctx.close_connections()


    def loop(self):

        while self.ctx.run == self.ctx.status_enum.RUNNING.value:
            
            self.ctx.authorization_check()
            if self.ctx.storage_api is None:
                continue

            assets = self.ctx.track_mongo.get_error_entries()

            if assets is None:
                time.sleep(180)
            else:
                errors_found = 0
                for asset in assets:

                    # let asset_job_error_handler handle jobs_status errors
                    if asset["jobs_status"] == self.ctx.status_enum.ERROR.value:
                        continue

                    errors_found += 1
                    
                    # erda_sync error
                    if asset[self.ctx.flag_enum.ERDA_SYNC.value] == self.ctx.status_enum.ERROR.value:
                        self.erda_sync_handler.handle_erda_sync_error(asset)
                    
                    # has_open_share error
                    if asset[self.ctx.flag_enum.HAS_OPEN_SHARE.value] == self.ctx.status_enum.ERROR.value:
                        self.has_open_share_handler.handle_has_open_share_error(asset)

                    # specify_sync error
                    if asset[self.ctx.flag_enum.SPECIFY_SYNC.value] == self.ctx.status_enum.ERROR.value:
                        self.specify_sync_handler.handle_specify_sync_error(asset)                    

                    # has_new_file error
                    if asset[self.ctx.flag_enum.HAS_NEW_FILE.value] == self.ctx.status_enum.ERROR.value:
                        self.has_new_file_handler.handle_has_new_file_error(asset)

                print(f"Assets with errors found: {errors_found}")
                time.sleep(60)

            #checks if service should keep running           
            self.ctx.run = self.ctx.run_util.check_run_changes()

            # Pause loop
            if self.ctx.run == self.ctx.status_enum.PAUSED.value:
                self.ctx.run = self.ctx.run_util.pause_loop()
        
        # out of main loop
        self.ctx.run_util.service_stopping_updates()
        self.ctx.close_connections()
        print("Service shut down")  

if __name__ == '__main__':
    AssetErrorStatusHandler()