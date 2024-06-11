import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
import time
from Enums import status_enum
from HealthUtility import health_caller
from InformationModule.log_class import LogClass

"""
Class that helps the micro services with logging and run status updates.
Takes the service name, run config path, log filename and the logger name as arguments.
Example: "Asset creator ARS", "root/ConfigFiles/run_config.json", "asset_creator.py.log", "asset_creator"
"""
class RunUtility(LogClass):

    def __init__(self, service_name, run_config_path, log_filename, logger_name):

        # setting up logging for service
        super().__init__(log_filename, logger_name)

        self.util = utility.Utility()
        self.status_enum = status_enum.StatusEnum
        self.health_caller = health_caller.HealthCaller()
        self.service_name = service_name
        self.run_config_path = run_config_path
        
        # flag for the all run status
        self.all_run_status = self.get_all_run()
        # flag for the specific service
        self.run_service = self.get_run_service()

        # combined run flag
        self.service_run = self.get_service_run_status()

    """
    Loop for services that have their status set to paused. 
    Keeps track of how long the pause lasts. 
    Pause time could be moved to a config file so it could be different for different services.
    Logs the pause warning and sends a message to the health api. 
    Returns the overall status of the service when it stops being in pause mode. 
    """
    def pause_loop(self):
        counter = 0
        # seconds to pause
        sleep = 10
        self.service_run = self.get_service_run_status()
        while self.service_run == self.status_enum.PAUSED.value:
                counter += 1
                time.sleep(sleep)
                wait_time = sleep * counter
                # TODO could make a util function for changing seconds into a better time format
                entry = self.log_msg(f"{self.service_name} has been in pause mode for: {wait_time} seconds")
                self.health_caller.warning(self.service_name, entry)
                
                self.service_run = self.check_run_changes()

        return self.service_run

    """
    Checks if service should keep running - configurable in ConfigFiles/run_config.json
    Logs and sends a warning message to the health api when run status changes
    Returns the overall run status for the service
    """
    def check_run_changes(self):
        # checks all run status               
        all_run = self.get_all_run()
        if self.all_run_status != all_run:
            entry = self.log_msg(f"All run status changed from {self.service_run} to {all_run}")
            self.health_caller.run_status_change(self.service_name, all_run, entry)

        # checks run service status
        run_service = self.get_run_service()
        if self.run_service != run_service:
            entry = self.log_msg(f"{self.service_name} status changed from {self.service_run} to {run_service}")
            self.health_caller.run_status_change(self.service_name, run_service, entry)
        
        # updates run status
        self.all_run_status = self.get_all_run()
        self.run_service = self.get_run_service()
        self.service_run = self.get_service_run_status()
        
        return self.service_run

    """
    get the all run status from the config file
    """
    def get_all_run(self):
        return self.util.get_value(self.run_config_path, "all_run")
    
    """
    get the specific service run status from the config file
    """
    def get_run_service(self):
        return self.util.get_value(self.run_config_path, self.service_name)
    
    """
    get the overall service run status
    """
    def get_service_run_status(self):

        all_run = self.get_all_run()
        service_run = self.get_run_service()

        if all_run == self.status_enum.STOPPED.value or service_run == self.status_enum.STOPPED.value:
            return self.status_enum.STOPPED.value
        
        if all_run == self.status_enum.PAUSED.value or service_run == self.status_enum.PAUSED.value:
            return self.status_enum.PAUSED.value

        return self.status_enum.RUNNING.value