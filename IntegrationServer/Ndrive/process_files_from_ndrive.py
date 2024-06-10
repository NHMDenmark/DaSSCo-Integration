import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from JobList import job_driver
import time
import utility
from InformationModule.log_class import LogClass
from HealthUtility import health_caller
from Enums import status_enum

"""
Class responsible for initiating the processing of new files from the ndrive. Specifically this means we have
both a json and an img file of some kind. Calls the JobDriver class for actual processing.
Logs warnings and errors from this process, and directs them to the health service.
"""

# TODO needs to decide if a timer or trigger system is needed here.


class ProcessNewFiles(LogClass):

    def __init__(self):
        
        # setting up logging
        super().__init__(filename = f"{os.path.basename(os.path.abspath(__file__))}.log", name = os.path.relpath(os.path.abspath(__file__), start=project_root))
        # service name for logging/info purposes
        self.service_name = "Process new files (Ndrive)"

        self.jobby = job_driver.JobDriver()
        self.run_config_path = f"{project_root}/ConfigFiles/run_config.json"
        self.new_files_path = f"{project_root}/Files/NewFiles"
        self.updated_files_path = f"{project_root}/Files/UpdatedFiles"
        self.health_caller = health_caller.HealthCaller()
        self.util = utility.Utility()
        self.status_enum = status_enum.StatusEnum

        # set the config file value to RUNNING, mostly for ease of testing
        self.util.update_json(self.run_config_path, self.service_name, self.status_enum.RUNNING.value)
        
        self.run = self.util.get_value(self.run_config_path, self.service_name)

        self.loop()

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:

            self.jobby.process_new_directories_from_ndrive()

            time.sleep(2)

            # checks if service should keep running - configurable in ConfigFiles/run_config.json            
            all_run = self.util.get_value(self.run_config_path, "all_run")
            service_run = self.util.get_value(self.run_config_path, self.service_name)

            # Pause loop
            counter = 0
            while service_run == self.status_enum.PAUSED.value:
                sleep = 10
                counter += 1
                time.sleep(sleep)
                wait_time = sleep * counter
                entry = self.log_msg(f"{self.service_name} has been in pause mode for ~{wait_time} seconds")
                self.health_caller.warning(self.service_name, entry)
                service_run = self.util.get_value(self.run_config_path, self.service_name)
                
                all_run = self.util.get_value(self.run_config_path, "all_run")
                if all_run == self.status_enum.STOPPED.value:
                    service_run = self.status_enum.STOPPED.value
                
                if service_run != self.status_enum.PAUSED.value:
                    entry = self.log_msg(f"{self.service_name} has changed run status from {self.status_enum.PAUSED.value} to {service_run}")                   
                    self.health_caller.warning(self.service_name, entry)

            if all_run == self.status_enum.STOPPED.value or service_run == self.status_enum.STOPPED.value:
                self.run = self.status_enum.STOPPED.value


if __name__ == '__main__':
    ProcessNewFiles()
