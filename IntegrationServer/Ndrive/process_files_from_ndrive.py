import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from AssetFileHandler import asset_handler
import time
import utility
from MongoDB import service_repository
from HealthUtility import health_caller, run_utility
from Enums import status_enum

"""
Class responsible for initiating the processing of new files from the ndrive. Specifically this means we have
both a json and an img file of some kind. Calls the JobDriver class for actual processing.
Logs warnings and errors from this process, and directs them to the health service.
"""

# TODO needs to decide if a timer or trigger system is needed here.


class ProcessNewFiles():

    def __init__(self):
        
        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)

        # service name for logging/info purposes
        self.service_name = "Process new files (Ndrive)"
        self.prefix_id = "Pnf(N)"

        self.asset_handler = asset_handler.AssetHandler()
        self.service_mongo = service_repository.ServiceRepository()
        self.new_files_path = f"{project_root}/Files/NewFiles"
        self.updated_files_path = f"{project_root}/Files/UpdatedFiles"
        self.health_caller = health_caller.HealthCaller()
        self.util = utility.Utility()
        self.status_enum = status_enum.StatusEnum
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

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:

            self.asset_handler.process_new_directories()

            time.sleep(2)

            # checks if service should keep running           
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.status_enum.PAUSED.value:
                self.run = self.run_util.pause_loop()
        
        # out of main loop
        self.service_mongo.close_connection()

if __name__ == '__main__':
    ProcessNewFiles()
