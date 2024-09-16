import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from datetime import datetime, timedelta
import utility
from MongoDB import service_repository, health_repository
from HealthUtility import health_caller, run_utility
from Enums import status_enum, validate_enum

"""
Service that checks if there are too many or too much asset in the pipeline at any one point. Will change the run_status of other services to throttle their input/output of assets.
"""
class ThrottleService():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        
        # service name for logging/info purposes
        self.service_name = "Throttle service"
        self.prefix_id= "Ths"

        self.util = utility.Utility()
        self.service_mongo = service_repository.ServiceRepository()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.Validate

        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name)

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

if __name__ == "__main__":
    ThrottleService()