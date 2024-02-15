import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import shutil
import time
import utility

"""
Class responsible for initiating the process of importing new files from the ndrive. 
Runs a loop that checks the ndrive for previously not imported files.
"""


class NdriveNewFilesFinder:

    def __init__(self):

        self.util = utility.Utility()

        self.new_files_path = "IntegrationServer/Files/NewFiles"
        self.workstations_config_path = "IntegrationServer/ConfigFiles/workstations_config.json"
        self.ndrive_import_path = self.util.get_value("IntegrationServer/ConfigFiles/ndrive_path_config.json", "ndrive_path")
        
        self.run = True
        self.count = 0

        self.loop()

    def loop(self):

        while self.run:

            self.copy_from_ndrive_and_update_ndrive_dirs(self.ndrive_import_path, self.new_files_path)

            time.sleep(3)

            self.count += 1

            if self.count > 2:
                # print("done", self.ndrive_import_path)
                self.run = False

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
                    error_directory_path = os.path.join("IntegrationServer/Files/Error", base_name)
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
    Renames the batch directory on the server the import was done from. Adds the prefix imported_ to the directory.
    """

    def rename_batch_directory_after_import(self, local_path):
        batch_name = os.path.basename(local_path)

        # Define the new path
        new_path = os.path.join(os.path.dirname(local_path), f"imported_{batch_name}")

        # Create the new directory
        os.makedirs(new_path, exist_ok=True)

        # Move contents from the old directory to the new one
        for item in os.listdir(local_path):
            old_item_path = os.path.join(local_path, item)
            new_item_path = os.path.join(new_path, item)
            shutil.copy(old_item_path, new_item_path)

        # Check if everything has been moved successfully
        old_contents = set(os.listdir(local_path))
        new_contents = set(os.listdir(new_path))

        if old_contents == new_contents:
            # If contents are the same, remove the old directory
            shutil.rmtree(local_path)
        else:
            for file in old_contents:
                print(file)
            for file in new_contents:
                print(file)
            # TODO Handle the case where not everything was moved successfully
            print(f"Error: Not all contents in {local_path} were successfully moved.")


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
