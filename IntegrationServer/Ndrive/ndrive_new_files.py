import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import shutil
import time
import utility
from InformationModule.log_class import LogClass
from HealthUtility import health_caller
from Enums import status_enum

"""
Class responsible for initiating the process of importing new files from the ndrive. 
Runs a loop that checks the ndrive for previously not imported files.
Logs warnings and errors from this process, and directs them to the health service.
"""
class NdriveNewFilesFinder(LogClass):

    def __init__(self):

        # setting up logging
        super().__init__(filename = f"{os.path.basename(os.path.abspath(__file__))}.log", name = os.path.relpath(os.path.abspath(__file__), start=project_root))
        # service name for logging/info purposes
        self.service_name = "New files finder (Ndrive)"

        self.util = utility.Utility()
        self.run_config_path = f"{project_root}/ConfigFiles/run_config.json"
        self.workstations_config_path = f"{project_root}/ConfigFiles/workstations_config.json"
        self.ndrive_import_path = self.util.get_value(f"{project_root}/ConfigFiles/ndrive_path_config.json", "ndrive_path")
        self.new_files_path = f"{project_root}/Files/NewFiles"
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum

        # set the config file value to RUNNING, mostly for ease of testing
        self.util.update_json(self.run_config_path, self.service_name, self.status_enum.RUNNING.value)
        
        self.run = self.util.get_value(self.run_config_path, self.service_name)
        self.loop()

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:

            self.copy_from_ndrive_and_update_ndrive_dirs(self.ndrive_import_path, self.new_files_path)

            time.sleep(1)

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
