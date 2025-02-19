import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from datetime import datetime, timedelta
import utility
from MongoDB import service_repository, throttle_repository
from HealthUtility import health_caller, run_utility
from Enums import status_enum, validate_enum

"""
Service that checks if there are too many or too much asset in the pipeline at any one point. Will change the run_status of other services to throttle their input/output of assets.
"""
# Not in use
class ThrottleService():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        
        # service name for logging/info purposes
        self.service_name = "Throttle service"
        self.prefix_id= "Ths"

        
        self.throttle_config_path = f"{project_root}/ConfigFiles/throttle_config.json"

        self.util = utility.Utility()
        self.service_mongo = service_repository.ServiceRepository()
        self.throttle_mongo = throttle_repository.ThrottleRepository()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.Validate

        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name)
        
        # sets default values
        self.max_total = 10
        self.total_size = 100000
        self.sync_max = 5
        # sets config values
        self.set_max_values()

        # set the service db value to RUNNING, mostly for ease of testing
        self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.RUNNING.value)
        
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        self.run = self.run_util.get_service_run_status()
        self.loop()

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            # check if number of in flight assets > max number of assets -> react


            pass
    
    def set_max_values(self):
        try:
            self.max_total = self.util.get_value(self.throttle_config_path, "assets_in_flight")
            self.total_size = self.util.get_value(self.throttle_config_path, "total_asset_size_mb")
            self.sync_max = self.util.get_value(self.throttle_config_path, "max_asset_sync_count")
        except Exception as e:
            print(f"Continuing with default or old values. {e}")

if __name__ == "__main__":
    ThrottleService()