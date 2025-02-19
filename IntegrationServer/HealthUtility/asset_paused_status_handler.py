import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from datetime import datetime, timedelta
import utility
from MongoDB import service_repository, track_repository
from HealthUtility import health_caller, run_utility
from Enums import status_enum, validate_enum, flag_enum

"""
Service that checks assets for having available_for_services set to PAUSED and sets their status to yes once the pause period is over. 
"""
class AssetPausedStatusHandler():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        
        # service name for logging/info purposes
        self.service_name = "Asset paused status handler"
        self.prefix_id= "Apsh"

        self.util = utility.Utility()
        
        self.service_mongo = service_repository.ServiceRepository()
        self.track_mongo = track_repository.TrackRepository()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.flag_enum = flag_enum.FlagEnum
        self.validate_enum = validate_enum.ValidateEnum
        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name)

        # set the service db value to RUNNING, mostly for ease of testing
        self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.RUNNING.value)
        
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

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
            self.close_all_connections()

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            assets = self.track_mongo.get_entries(self.flag_enum.AVAILABLE_FOR_SERVICES.value, self.status_enum.PAUSED.value)

            if assets == []:
                self.end_of_loop_checks()
                continue

            current_time = datetime.now()

            for asset in assets:

                guid = asset["_id"]

                if asset[self.flag_enum.AVAILABLE_FOR_SERVICES_TIMESTAMP.value] is None or asset[self.flag_enum.AVAILABLE_FOR_SERVICES_WAIT_TIME.value] is None:
                    self.track_mongo.update_entry(guid, self.flag_enum.AVAILABLE_FOR_SERVICES.value, self.status_enum.ERROR.value)
                    entry = self.run_util.log_msg(self.prefix_id, f"Missing timestamp or wait time so set AVAILABLE_FOR_SERVICE to ERROR for {guid}", self.validate_enum.ERROR.value)
                    self.health_caller.error(self.service_name, entry, guid)
                    print(f"Missing data for timestamp or wait time for {guid}")
                    continue

                passed_time = current_time - asset[self.flag_enum.AVAILABLE_FOR_SERVICES_TIMESTAMP.value]

                if passed_time > timedelta(seconds=asset[self.flag_enum.AVAILABLE_FOR_SERVICES_WAIT_TIME.value]):

                    self.track_mongo.update_entry(guid, self.flag_enum.AVAILABLE_FOR_SERVICES_WAIT_TIME.value, None)
                    self.track_mongo.update_entry(guid, self.flag_enum.AVAILABLE_FOR_SERVICES_TIMESTAMP.value, None)
                    self.track_mongo.update_entry(guid, self.flag_enum.AVAILABLE_FOR_SERVICES.value, self.validate_enum.YES.value)
                    print(f"{guid} had available_for_service set to YES")

            self.end_of_loop_checks()
        
        # out of main loop
        self.close_all_connections()
        print("Service has shut down")

    def close_all_connections(self):

        self.service_mongo.close_connection()
        self.track_mongo.close_connection()

    def end_of_loop_checks(self):
        #checks if service should keep running           
        self.run = self.run_util.check_run_changes()

        # Pause loop
        if self.run == self.status_enum.PAUSED.value:
            self.run = self.run_util.pause_loop()
        
        time.sleep(30)

if __name__ == '__main__':
    AssetPausedStatusHandler()