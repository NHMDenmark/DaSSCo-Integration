import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from HealthUtility import health_caller, run_utility
from Enums import status_enum, validate_enum, flag_enum, asset_status_nt
## other imports

"""
Description 
"""
class ServiceSkeleton():

    def __init__(self):
        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        self.pid = os.getpid()
        # service name for logging/info purposes
        self.service_name = "Service skeleton"
        self.prefix_id= "SS"

        self.util = utility.Utility()
        self.health_caller = health_caller.HealthCaller()
        self.flag_enum = flag_enum.FlagEnum
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum
        self.asset_status_enum = asset_status_nt.AssetStatusNT
        # other initialisations, db connections, enums etc

        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name, self.pid)
        
        self.run_util.service_starting_updates()
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
            self.run_util.service_stopping_updates()
            self.close_all_connections()

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            # main loop code here            
            
            # check if while loop continues
            self.end_of_loop_checks()

        # out of main loop
        self.run_util.service_stopping_updates()
        self.close_all_connections()
        print("Service shut down")

    def close_all_connections(self):
        # close any db connections here
        pass

    def end_of_loop_checks(self):
        # checks if service should keep running           
        self.run = self.run_util.check_run_changes()

        # Pause loop
        if self.run == self.status_enum.PAUSED.value:
            self.run = self.run_util.pause_loop()

if __name__ == '__main__':
    ServiceSkeleton()