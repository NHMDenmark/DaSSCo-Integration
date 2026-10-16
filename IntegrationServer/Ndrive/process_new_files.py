import sys
import os
from dotenv import load_dotenv

script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from AssetFileHandler import asset_handler_two
import time
import utility
from HealthUtility import health_caller, run_utility
from Enums import status_enum
from MongoDB.mongo_connection import MongoSharedClient
from IntegrationServer.MongoDB import track_repository, throttle_repository

"""
Class responsible for initiating the processing of new files from the ndrive. Specifically this means we have
both a json and an img file of some kind. Calls the JobDriver class for actual processing.
Logs warnings and errors from this process, and directs them to the health service.
"""

# TODO needs to decide if a timer or trigger system is needed here. 
# also may want to check throttle for total assets in system before processing new assets.

class ProcessNewFiles():

    def __init__(self):

        load_dotenv()
        
        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        self.pid = os.getpid()
        # service name for logging/info purposes
        self.service_name = "Process new files"
        self.prefix_id = "Pnf"

        self.workstations_config_path = f"{project_root}/ConfigFiles/workstations_config.json"
        self.base_import_path = os.getenv("NDRIVE_PATH")

        self.mongo_client = MongoSharedClient()
        self.throttle_mongo = throttle_repository.ThrottleRepository(self.mongo_client)
        self.track_mongo = track_repository.TrackRepository(self.mongo_client)
        self.health_caller = health_caller.HealthCaller()
        self.util = utility.Utility()
        self.status_enum = status_enum.StatusEnum
        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name, self.pid, self.mongo_client)
        
        self.asset_handler = asset_handler_two.AssetHandlerTwo(self.run_util, self.mongo_client)

        self.run_util.service_starting_updates()        
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        self.run = self.run_util.get_service_run_status()

        try:
            self.loop()
        except Exception as e:
            print("service crashed", e)
            try:
                entry = self.run_util.log_exc(self.prefix_id, f"{self.service_name} crashed. Make sure to check if the last asset is in an ok state. Its possible for assets to get stuck here if the creation process goes wrong.", e, self.status_enum.CRITICAL_ERROR.value)
                self.health_caller.unexpected_error(self.service_name, entry)
            except:
                print(f"failed to inform about crash")
            self.run_util.service_stopping_updates()
            self.close_db_connections()

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:

            # Finds an unimported directory
            import_directory = self.get_batch_directory_path(self.base_import_path)

            if import_directory is None:
                time.sleep(30)
                self.end_of_loop_checks()
                continue

            # process new assets in the from a directory
            processed = self.asset_handler.process_new_assets(import_directory)

            # update the import directory name to reflect that it has been imported. This is done to prevent the same directory from being processed again.
            if processed:
                self.rename_batch_directory_after_import(import_directory)
                print(f"processed: {import_directory}")

            time.sleep(2)
            self.end_of_loop_checks()
        
        # out of main loop
        self.run_util.service_stopping_updates()
        self.close_db_connections()
        print("service closed")

    def close_db_connections(self):
        try:
            self.mongo_client.close()
        except Exception as e:  
            print(f"Failed to close db connections: {e}")


    def end_of_loop_checks(self):
        # checks if service should keep running           
        self.run = self.run_util.check_run_changes()
        
        # Pause loop
        if self.run == self.status_enum.PAUSED.value:
            self.run = self.run_util.pause_loop()

    """
    Renames the batch directory on the direcory the import was done from. As default adds the prefix imported_ to the directory.
    """
    def rename_batch_directory_after_import(self, import_directory, prefix = "imported_"):
        
        new_base_path, guid = os.path.split(import_directory)
        
        # Define the new path
        new_path = os.path.join(new_base_path, f"{prefix}{guid}")
        print(f"Renaming directory from {import_directory} to {new_path}")
        # Rename the directory
        os.rename(import_directory, new_path)

    """
    Find a unimported batch directory directory path based on the keys found in the workstation config file.
    Will only return one batch directory path even if multiple exists. 
    """
    def get_batch_directory_path(self, remote_folder):
        # Read workstation configuration data from JSON file
        workstations_config_data = self.util.read_json(self.workstations_config_path)
        
        # Get a list of keys from the workstation configuration data
        workstation_list = list(workstations_config_data.keys())

        # Iterate over directories in remote_folder
        for directory in os.listdir(remote_folder):
            # Check if the directory has the same name as one of the keys in workstation_list
            if directory in workstation_list:
                # Further check for subdirectories
                subdirectories = os.listdir(f"{remote_folder}/{directory}")

                # Check for subdirectories that do not start with "imported_" or "error_" or "new_" ("new" is used by the test script that creates new assets to prevent picking up the folder mid creation)
                for subdirectory in subdirectories:
                    
                    if not subdirectory.startswith("imported_") and not subdirectory.startswith("error_") and not subdirectory.startswith("new_"):
                        print(f"{remote_folder}/{directory}/{subdirectory}")
                        return f"{remote_folder}/{directory}/{subdirectory}"
        # If no matching directory is found
        return None

if __name__ == '__main__':
    ProcessNewFiles()