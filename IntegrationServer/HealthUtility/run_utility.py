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
from StorageApi import storage_client, ars_health_check

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
        self.ars_health_check = ars_health_check.ArsHealthCheck()
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
    Pause times are in a config file so it could be different for different services.
    Logs the pause warning and sends a message to the health api. 
    Returns the overall status of the service when it stops being in pause mode. 
    """
    def pause_loop(self):
        counter = 0
        # seconds to pause
        sleep = self.util.get_nested_value(self.micro_service_config_path, self.service_name, "pause_time")
        pause_check_list = self.util.get_nested_value(self.micro_service_config_path, self.service_name, "pause_check_list")
        pause_loop_count = self.util.get_nested_value(self.micro_service_config_path, self.service_name, "pause_loop_count")
        self.service_run = self.get_service_run_status()
        while self.service_run == self.PAUSED:
                counter += 1
                time.sleep(sleep)
                wait_time = sleep * counter
                # TODO could make a util function for changing seconds into a better time format

                loop_message = f"{self.service_name} has been in pause mode for: {wait_time} seconds"
                
                if counter in pause_check_list or counter % pause_loop_count == 0:
                    self.attempt_unpause(counter)
                else:
                    entry = self.log_msg(self.prefix_id, loop_message)
                    self.health_caller.create_health_entry(self.service_name, entry)

                self.service_run = self.check_run_changes()

        return self.service_run
    
    """
    # TODO desc, logic etc
    """
    def attempt_unpause(self, pause_count: int):

        paused = True
        extra_msg = ""

        # get the module the service belongs to, then call the corresponding check for unpause routine
        module = self.util.get_nested_value(self.micro_service_config_path, self.service_name, "module")

        if module == "ssh hpc":
            paused, extra_msg = self.ssh_hpc_unpause_routine(self.service_name)

        if module == "storage updater":
            paused, extra_msg = self.storage_updater_unpause_routine(self.service_name)
            
        if module == "ndrive":
            paused, extra_msg = self.ndrive_unpause_routine(self.service_name)

        if module == "asset file handler":
            paused, extra_msg = self.asset_file_handler_unpause_routine(self.service_name)

        if module == "health utility":
            paused, extra_msg = self.health_utility_unpause_routine(self.service_name)

        if module == "tests":
            paused, extra_msg = self.tests_unpause_routine(self.service_name)
            
        if paused is True: 
            message = f"{self.service_name} attempted and failed to unpause. This was attempted after {pause_count} pause loops. {extra_msg}"

            entry = self.log_msg(self.prefix_id, message)
            self.health_caller.attempted_unpause(self.service_name, self.PAUSED, pause_count, entry)

        if paused is False:
            self.service_run = self.check_run_changes()
            message = f"{self.service_name} unpaused. This was after {pause_count} pause loops. Status is now {self.service_run}."

            entry = self.log_msg(self.prefix_id, message)
            self.health_caller.attempted_unpause(self.service_name, self.service_run, pause_count, entry)

    """
    Logs and sends a warning message to the health api when run status changes
    Returns the overall run status for the service
    """
    def check_run_changes(self):
        # checks all run status               
        all_run = self.get_all_run()
        if self.all_run_status != all_run:
            self.log_all_run_status_change(self.all_run_status, all_run)

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
            self.health_caller.run_status_change(self.service_name, new_status, entry)

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
    
    def storage_updater_unpause_routine(self, service_name):
        
        stay_paused = True

        try:
            storage_api = storage_client.StorageClient()
         
            if storage_api.client is None:
                return stay_paused, "Failed to create a new storage client."
            
        except Exception as e:
            entry = self.log_exc(self.prefix_id, f"Error while attempting unpause routine for {service_name}", level=self.ERROR, exc=e)
            self.health_caller.unexpected_error(service_name, entry)
            return stay_paused, "Unexpected error while attempting to create a new storage client. This error has also been logged separately."

        # query ARS for their status
        try:
            ars_status = self.check_ars_total_health_status()
            
            if ars_status is False:
                return stay_paused, "ARS or keycloak up status failed."

        except Exception as e:
            entry = self.log_exc(self.prefix_id, f"Error while attempting unpause routine for {service_name}", level=self.ERROR, exc=e)
            self.health_caller.unexpected_error(service_name, entry)
            return stay_paused, "Unexpected error while attempting to get ARS/keycloak health status. This error has also been logged separately."

        # check open/close share, file upload/download 


        # check if last error has an asset guid attached
        # check if asset data is fine both in ars and int server

        # TODO more logic
        try:
            pass
        except Exception as e:
            pass

        return stay_paused, "This module is unable to unpause itself. Requires manual intervention."
    
    def ndrive_unpause_routine(self, service_name):

        stay_paused = True
        # TODO more logic
        return stay_paused, "This module is unable to unpause itself. Requires manual intervention."
    
    def health_utility_unpause_routine(self, service_name):

        stay_paused = True
        # TODO more logic
        return stay_paused, "This module is unable to unpause itself. Requires manual intervention."
    
    def ssh_hpc_unpause_routine(self, service_name):

        stay_paused = True
        # TODO more logic
        return stay_paused, "This module is unable to unpause itself. Requires manual intervention."
    
    def asset_file_handler_unpause_routine(self, service_name):

        stay_paused = True
        # TODO more logic
        return stay_paused, "This module is unable to unpause itself. Requires manual intervention."
    
    def tests_unpause_routine(self, service_name):
        # Always unpauses
        stay_paused = False
        
        return stay_paused, ""
    
    # Checks the up status for ARS and keycloak. Returns True if all status are up and False otherwise.
    def check_ars_total_health_status(self):
        
        ars_check = self.ars_health_check.check_asset_service_health()
        keycloak_check = self.ars_health_check.check_keycloak_health()
        fileproxy_check = self.ars_health_check.check_fileproxy_health()

        if False in [ars_check, keycloak_check, fileproxy_check]:
            return False
        
        return True
