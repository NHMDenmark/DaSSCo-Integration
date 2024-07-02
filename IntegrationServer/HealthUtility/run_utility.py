import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
import time
from MongoDB import service_repository
from Enums.status_enum import Status
from HealthUtility import health_caller
from InformationModule.log_class import LogClass

"""
Class that helps the micro services with logging, pausing and run status updates.
Takes the prefix_id, service name, log filename and the logger name as arguments.
Example: "AcA", "Asset creator ARS", "asset_creator.py.log", "asset_creator"
"""
class RunUtility(LogClass, Status):

    def __init__(self, prefix_id, service_name, log_filename, logger_name):

        LogClass.__init__(self, log_filename, logger_name)
        Status.__init__(self)

        self.micro_service_config_path = f"{project_root}/ConfigFiles/micro_service_config.json"
        self.util = utility.Utility()
        self.service_mongo = service_repository.ServiceRepository()
        self.health_caller = health_caller.HealthCaller()
        self.service_name = service_name
        self.prefix_id = prefix_id
        
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
        sleep = self.util.get_nested_value(self.micro_service_config_path, self.service_name, "pause_time")
        self.service_run = self.get_service_run_status()
        while self.service_run == self.PAUSED:
                counter += 1
                time.sleep(sleep)
                wait_time = sleep * counter
                # TODO could make a util function for changing seconds into a better time format

                loop_message = f"{self.service_name} has been in pause mode for: {wait_time} seconds"
                
                # TODO could make the numbers configurable in the micro service config file
                if counter == 5:
                    self.attempt_unpause(counter)
                elif counter == 23:
                    self.attempt_unpause()
                elif counter%99 == 0:
                     self.attempt_unpause()
                else:
                    entry = self.log_msg(self.prefix_id, loop_message)
                    self.health_caller.warning(self.service_name, entry)


                self.service_run = self.check_run_changes()

        return self.service_run
    
    """
    # TODO desc, logic etc
    """
    def attempt_unpause(self, pause_count: int):

        paused = True

        # TODO check which module the service belongs to. Then create specific check for different modules. Add module to service config file?
        module = self.util.get_nested_value(self.micro_service_config_path, self.service_name, "module")

        
        if paused is True: 
            message = f"{self.service_name} attempted and failed to unpause. This was attempted after {pause_count} loop counts."

            entry = self.log_msg(self.prefix_id, message)
            self.health_caller.attempted_unpause(self.service_name, self.PAUSED, pause_count, entry)


        if paused is False:
            self.service_run = self.check_run_changes()
            message = f"{self.service_name} attempted and succeeded to unpause. This was after {pause_count} loop counts. Status is now {self.service_run}."

            entry = self.log_msg(self.prefix_id, message)
            self.health_caller.attempted_unpause(self.service_name, self.service_run, pause_count, entry)

    """
    Checks if service should keep running - configurable in ConfigFiles/run_config.json
    Logs and sends a warning message to the health api when run status changes
    Returns the overall run status for the service
    """
    def check_run_changes(self):
        # checks all run status               
        all_run = self.get_all_run()
        if self.all_run_status != all_run:
            entry = self.log_msg("All", f"All run status changed from {self.service_run} to {all_run}")
            self.health_caller.run_status_change(self.service_name, all_run, entry)

        # checks run service status
        run_service = self.get_run_service()
        if self.run_service != run_service:
            self.log_status_change(self.service_name, self.service_run, run_service)
        
        # updates run status
        self.all_run_status = self.get_all_run()
        self.run_service = self.get_run_service()
        self.service_run = self.get_service_run_status()
        
        return self.service_run
    
    """
    logs a status change for all_run and calls the health api
    """
    def log_all_run_status_change(self, old_status, new_status):
            entry = self.log_msg("All", f"All run status changed from {old_status} to {new_status}")
            self.health_caller.run_status_change("No name", new_status, entry)

    """
    logs a status change and calls the health api
    """
    def log_status_change(self, service_name, old_status, new_status):
        entry = self.log_msg(self.prefix_id, f"{service_name} status changed from {old_status} to {new_status}")
        self.health_caller.run_status_change(service_name, new_status, entry)


    """
    get the all run status from the mongo db
    """
    def get_all_run(self):
        return self.service_mongo.get_value_for_key("all_run", "run_status")
    
    """
    get the specific service run status from the mongo db
    """
    def get_run_service(self):
        return self.service_mongo.get_value_for_key(self.service_name, "run_status")
    
    """
    get the overall service run status
    """
    def get_service_run_status(self):

        all_run = self.get_all_run()
        service_run = self.get_run_service()

        if all_run == self.STOPPED or service_run == self.STOPPED:
            return self.STOPPED
        
        if all_run == self.PAUSED or service_run == self.PAUSED:
            return self.PAUSED

        return self.RUNNING