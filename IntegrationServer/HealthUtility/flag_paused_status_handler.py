import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from datetime import datetime, timedelta
import utility
from MongoDB import service_repository, track_repository, health_repository
from HealthUtility import health_caller, run_utility
from Enums import status_enum, validate_enum, flag_enum

"""
Service that checks assets for having flag status set to PAUSED.
Then resets their status after 10 minutes to the previous value, probably NO but could be anything.
Requires the temporary fields: temp_timeout_status, temp_timeout_timestamp, temp_previous_flag_value
Removes the temporary fields that was added to the track entries when a pause status is set.
Logs the reset process at the warning level.
"""
class FlagPausedStatusHandler():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        
        # service name for logging/info purposes
        self.service_name = "Flag paused status handler"
        self.prefix_id= "Fpsh"

        self.util = utility.Utility()
        
        self.service_mongo = service_repository.ServiceRepository()
        self.track_mongo = track_repository.TrackRepository()
        self.health_mongo = health_repository.HealthRepository()
        self.health_caller = health_caller.HealthCaller()
        self.flag_enum = flag_enum.FlagEnum
        self.status_enum = status_enum.StatusEnum
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
            self.close_all_connections()
            print("service crashed", e)

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            assets = self.track_mongo.get_paused_entries()

            if assets == []:
                # Total wait time is 1 min if no assets found 30 + 30 from end of loop check
                time.sleep(30)
                self.end_of_loop_checks()
                continue

            for asset in assets:
                
                guid = asset["_id"]

                if asset["temp_timeout_status"]:
                    
                    current_time = datetime.now()
                    passed_time = current_time - asset["temp_timeout_timestamp"]

                    # Check if 10 minutes has passed since the pause status was set
                    # TODO possible we want this to be more dynamic and part of configuration
                    if passed_time > timedelta(minutes=10):
                        
                        # Get the flag 
                        key = self.util.find_key_by_value(asset, self.validate_enum.PAUSED.value)
                        
                        # Reset value for flag
                        value = asset["temp_timeout_previous_flag_value"]

                        # Get rid of temp fields
                        self.remove_temp_fields(guid)

                        # Reset the flag value form paused to its previous value
                        self.track_mongo.update_entry(guid, key, value)

                        entry = self.run_util.log_msg(self.prefix_id, f"Reset the status of {guid} from PAUSED to {value} for {key}")
                        self.health_caller.warning(self.service_name, entry, guid)

                        print(f"Unpaused {guid} after {passed_time}")

                    else:
                        print(f"Still paused {guid}")

            self.end_of_loop_checks()
        
        # out of main loop
        self.close_all_connections()
        print("Service was shut down")

    def remove_temp_fields(self, guid):

        self.track_mongo.delete_field(guid, "temp_timeout_status")
        self.track_mongo.delete_field(guid, "temp_timeout_timestamp")
        self.track_mongo.delete_field(guid, "temp_timeout_previous_flag_value")

    def close_all_connections(self):

        self.service_mongo.close_connection()
        self.track_mongo.close_connection()
        self.health_mongo.close_connection()

    def end_of_loop_checks(self):
        #checks if service should keep running           
        self.run = self.run_util.check_run_changes()

        # Pause loop
        if self.run == self.status_enum.PAUSED.value:
            self.run = self.run_util.pause_loop()
        
        time.sleep(30)

if __name__ == '__main__':
    FlagPausedStatusHandler()