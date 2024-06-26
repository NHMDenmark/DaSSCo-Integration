import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import shutil
import time
import utility
from MongoDB import service_repository
from HealthUtility import health_caller, run_utility
from Enums import status_enum

"""
Class responsible for initiating the process of importing new files from the ndrive. 
Runs a loop that checks the ndrive for previously not imported files.
Logs warnings and errors from this process, and directs them to the health service.
"""
class NdriveNewFilesFinder():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        
        # service name for logging/info purposes
        self.service_name = "New files finder (Ndrive)"
        self.prefix_id= "Nff(N)"

        self.util = utility.Utility()
        
        self.workstations_config_path = f"{project_root}/ConfigFiles/workstations_config.json"
        self.ndrive_import_path = self.util.get_value(f"{project_root}/ConfigFiles/ndrive_path_config.json", "ndrive_path")
        self.new_files_path = f"{project_root}/Files/NewFiles"
        self.service_mongo = service_repository.ServiceRepository()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name)

       # set the service db value to RUNNING, mostly for ease of testing
        self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.RUNNING.value)
        
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        self.run = self.run_util.get_service_run_status()
        self.loop()

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:

            self.copy_from_ndrive_and_update_ndrive_dirs(self.ndrive_import_path, self.new_files_path)

            time.sleep(1)

           # checks if service should keep running           
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.status_enum.PAUSED.value:
                self.run = self.run_util.pause_loop()
        
        # out of main loop
        self.service_mongo.close_connection()
                

    def copy_from_ndrive_and_update_ndrive_dirs(self, ndrive_path, local_destination):

        # Finds an unimported batch directory
        remote_folder = self.get_batch_directory_path(ndrive_path)

        if remote_folder is not None:

            try:
                # List files in the remote folder
                files = [file for file in os.listdir(remote_folder)]

                # Group files by their base names
                file_groups = {}
                for file in files:
                    base_name, file_type = os.path.splitext(file)
                    if base_name not in file_groups:
                        file_groups[base_name] = []
                    file_groups[base_name].append((file, file_type))

                # Create local folders and copy files
                for base_name, file_list in file_groups.items():

                    # Check if a directory with the same base_name already exists in the Error directory
                    error_directory_path = os.path.join(f"{project_root}/Files/Error", base_name)
                    if os.path.exists(error_directory_path) and os.path.isdir(error_directory_path):
                        print(f"Directory {error_directory_path} already exists in the Error path. Skipping copy.")
                    else:
                        local_folder = os.path.join(local_destination, base_name)
                        os.makedirs(local_folder, exist_ok=True)

                        # Copy the files
                        for file, file_type in file_list:
                            local_path = os.path.join(local_folder, file)
                            remote_path = os.path.join(remote_folder, file)

                            shutil.copy(remote_path, local_path)

                print(f"Copy successful from {remote_folder} to {local_destination}.")

                self.rename_batch_directory_after_import(remote_folder)

            except Exception as e:
                print(f"An error occurred: {e}")

    """
    Renames the batch directory on the direcory the import was done from. Adds the prefix imported_ to the directory.
    """

    def rename_batch_directory_after_import(self, local_path):
        batch_name = os.path.basename(local_path)

        # Define the new path
        new_path = os.path.join(os.path.dirname(local_path), f"imported_{batch_name}")
        old_path = os.path.join(os.path.dirname(local_path), batch_name)

        # Rename the directory
        os.rename(old_path, new_path)

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

                # Check for subdirectories that do not start with "imported_"
                for subdirectory in subdirectories:
                    if not subdirectory.startswith("imported_"):
                        return f"{remote_folder}/{directory}/{subdirectory}"
        # If no matching directory is found
        return None


if __name__ == '__main__':
    NdriveNewFilesFinder()
