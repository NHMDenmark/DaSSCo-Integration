import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import paramiko
import stat
from utility import Utility


"""
Class that creates a ssh connection. Includes function to make use of the connection. 
Transfers files to and from the integration server through sftp. 
Sends commands directly through ssh connection.
Needs ssh keys to avoid password prompts. 
"""


class SSHConnection:
    def __init__(self, name, host, port, username, password):
        self.util = Utility()
        self.sftp = None
        self.name = name
        self.host = host
        self.port = port
        self.config_path = f"/work/data/DaSSCo-Integration/IntegrationServer/ConfigFiles/{self.name}_connection_config.json"
        self.status = ""
        self.is_slurm = ""
        self.new_import_directory_path = ""
        self.updated_import_directory_path = ""
        self.export_directory_path = ""
        self.username = username
        self.password = password
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect()
    """
    Creates the ssh connection based on host, port username and password. Sets up sftp. 
    Updates the status of the connection config file. 
    """
    def connect(self):
        # need if statement, checking status for open already -  get specific value from json

        try:
            self.ssh_client.connect(self.host, self.port, self.username, self.password)
            print(f"connected to {self.name}")

            self.util.update_layered_json(self.config_path, [self.name, "status"], "open")
            self.sftp = self.get_sftp()

        except Exception as e:
            print(f"Connection failed: {e}")

    """
    Closes a ssh connection. 
    """

    def close(self):
        try:
            self.sftp.close()
            self.ssh_client.close()
            self.util.update_layered_json(self.config_path, [self.name, "status"], "closed")
            print(f"closed {self.name}")
        except Exception as e:
            print(f"There was no connection: {e}")

    """
    Copies a file using sftp.
    """
    def sftp_copy_file(self, path_to_copy_from, path_to_copy_to):
        try:
            self.sftp.put(path_to_copy_from, path_to_copy_to)
            return True
        except Exception as e:
            print(path_to_copy_from, path_to_copy_to)
            return e
        
    """
    Creates a directory in another directory using sftp. Returns True if created or if directory already exists and False if failed to create.
    """
    def sftp_create_directory(self, directory_path, new_directory ):
        try:
            
            self.sftp.chdir(directory_path)
            
            try:
                self.sftp.chdir(f"{directory_path}/{new_directory}")
                self.sftp.chdir(None)
                return True
            
            except:
                # Create the directory using SFTP   
                self.sftp.mkdir(new_directory)

                self.sftp.chdir(None)
                return True

        except Exception as e:
            print(f"failed to create directories: {e}")
            return False
    
    """
    Iterates through each directory matching with a pipeline name found in the config files.
    Then looks for one without the imported_ prefix and returns directory as a path.
    """

    def get_batch_directory_path(self, remote_folder):
        # Read pipeline configuration data from JSON file
        pipeline_job_config_data = self.util.read_json("./ConfigFiles/pipeline_job_config.json")

        # Get a list of keys from the pipeline configuration data
        pipeline_list = list(pipeline_job_config_data.keys())

        # Iterate over directories in remote_folder
        for directory in self.sftp.listdir(remote_folder):
            # Check if the directory has the same name as one of the keys in pipeline_list
            if directory in pipeline_list:
                # Further check for subdirectories
                subdirectories = self.sftp.listdir(f"{remote_folder}/{directory}")

                # Check for subdirectories that do not start with "imported_"
                for subdirectory in subdirectories:
                    if not subdirectory.startswith("imported_"):
                        return f"{remote_folder}/{directory}/{subdirectory}"
        # If no matching directory is found
        return None

    """
    Function for importing a directory and sorting files into correct new/{guid}/* folders from ndrive.
    """

    def import_and_sort_files(self, remote_folder, local_destination):

        # Finds an unimported batch directory
        remote_folder = self.get_batch_directory_path(remote_folder)

        try:
            # List files in the remote folder
            files = [file for file in self.sftp.listdir(remote_folder)]

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
                error_directory_path = os.path.join("./Files/Error", base_name)
                if os.path.exists(error_directory_path) and os.path.isdir(error_directory_path):
                    print(f"Directory {error_directory_path} already exists in the Error path. Skipping copy.")
                else:
                    local_folder = os.path.join(local_destination, base_name)
                    os.makedirs(local_folder, exist_ok=True)

                    for file, file_type in file_list:
                        local_path = os.path.join(local_folder, file)
                        remote_path = os.path.join(remote_folder, file)

                        # Check if the file is a regular file
                        if stat.S_ISREG(self.sftp.stat(remote_path).st_mode):
                            # Copy the file from the server to the local machine
                            self.sftp.get(remote_path, local_path)

            print(f"Copy successful from {remote_folder} to {local_destination}.")

            self.rename_batch_directory_after_import(remote_folder)

        except Exception as e:
            print(f"An error occurred: {e}")

    """
    Renames the batch directory on the server the import was done from. Adds the prefix imported_ to the directory.
    """

    def rename_batch_directory_after_import(self, remote_path):

        batch_name = os.path.basename(remote_path)

        # Define the new path
        new_path = os.path.join(os.path.dirname(remote_path), f"imported_{batch_name}")

        # Create the new directory
        self.sftp.mkdir(new_path)

        # Move contents from the old directory to the new one
        for item in self.sftp.listdir(remote_path):
            old_item_path = os.path.join(remote_path, item)
            new_item_path = os.path.join(new_path, item)
            self.sftp.rename(old_item_path, new_item_path)

            # Check if everything has been copied successfully
        old_contents = set(self.sftp.listdir(remote_path))
        new_contents = set(self.sftp.listdir(new_path))

        if old_contents == new_contents:
            # If contents are the same, remove the old directory
            self.sftp.rmdir(remote_path)
        else:
            # TODO Handle the case where not everything was copied successfully
            print("Error: Not all contents were successfully copied.")

    """
    Copies files from the integration server onto another server through ssh/sftp. Usually this would be used for
    sending files to the slurm server. 
    """

    def sftp_export_directory_to_server(self, path_to_copy_from, path_to_copy_to):

        try:
            # Extract the last part of the source directory path
            source_directory_name = os.path.basename(os.path.normpath(path_to_copy_from))

            # Create a new directory in the destination with the same name
            destination_directory = os.path.join(path_to_copy_to, source_directory_name)

            # self.ssh_command(f"mkdir {path_to_copy_to}/{source_directory_name}")
            self.sftp.mkdir(f"{path_to_copy_to}/{source_directory_name}")
            # List all files in the source directory
            files_to_copy = os.listdir(path_to_copy_from)

            for file in files_to_copy:
                source_path = os.path.join(path_to_copy_from, file)
                destination_path = os.path.join(destination_directory, file)

                # Copy the file
                self.sftp.put(source_path, f"{path_to_copy_to}/{source_directory_name}/{file}")

                print(f"Copy successful: {source_path} to {destination_path}")

        except Exception as e:
            print(f"An error occurred exporting dir to server: {e}")

    """
    Copies files from a remote server onto integration server. Main use is getting new files from Ndrive currently.     
    """

    def sftp_import_directory_from_server(self, path_to_copy_from_server, path_to_copy_to_local):

        try:
            for directory in self.sftp.listdir(path_to_copy_from_server):
                # Extract the last part of the source directory path on the server
                source_directory_name = os.path.basename(os.path.normpath(directory))
                directory_path_to_copy = os.path.join(path_to_copy_from_server, source_directory_name)
                # Create a new directory locally with the same name
                local_destination_directory = os.path.join(path_to_copy_to_local, source_directory_name)

                if os.path.exists(local_destination_directory):
                    print(f"Skipping updated import: {local_destination_directory} already exists.")
                    continue

                os.makedirs(local_destination_directory, exist_ok=True)

                # Copy the directory from the server
                for item in self.sftp.listdir_attr(directory_path_to_copy):
                    source_path = os.path.join(directory_path_to_copy, item.filename)
                    relative_path = os.path.relpath(source_path, directory_path_to_copy)

                    local_destination_path = os.path.join(local_destination_directory, relative_path)
                    # Copy the file from the server to the local machine
                    print(source_path, local_destination_path, source_directory_name)
                    self.sftp.get(source_path, local_destination_path)

                print(f"Copy successful: {path_to_copy_from_server} to {local_destination_directory}")
        except Exception as e:
            print(f"An error occurred: {e}")

    """
    Checks that transferred files matches files from where they came from. 
    """

    def sftp_check_files_are_transferred(self, local_path, remote_path):
        try:
            # List files in the remote directory
            remote_files = self.sftp.listdir(remote_path)

            # List files in the local directory
            local_files = os.listdir(local_path)

            # Iterate over local files and check if they exist remotely and have the same checksum
            for local_file in local_files:
                local_file_path = os.path.join(local_path, local_file)

                # Check if the file exists remotely
                if local_file not in remote_files:
                    print(f"Error: {local_file} not found in remote directory.")
                    continue

                # Calculate checksum for the local file
                local_checksum = self.util.calculate_sha256_checksum(local_file_path)

                # Calculate checksum for the remote file
                remote_file_path = os.path.join(remote_path, local_file)
                remote_checksum = self.util.calculate_sha256_checksum(remote_file_path)

                # Compare checksums
                if local_checksum != remote_checksum:
                    print(f"Error: Checksums do not match for {local_file}.")
                    self.ssh_command(f"rm -r {remote_path}")
                    # TODO send local_path to error folder
                else:
                    print("good job")
        except Exception as e:
            print(f"Error: {e}")
            self.ssh_command(f"rm -r {remote_path}")
            # TODO send local_path to error folder

    def sftp_move(self, path_to_move_from, path_to_move_to):
        try:
            self.sftp.rename(path_to_move_from, path_to_move_to)
        except Exception as e:
            print(f"An error occurred: {e}")

    def sftp_delete(self, path_to_delete):
        try:
            self.sftp.remove(path_to_delete)
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_sftp(self):
        return self.ssh_client.open_sftp()

    """
    Function that allows remote commands to be used through connection. Gives option of writing output somewhere if needed. Returns output. 
    """

    def ssh_command(self, command, write_to_path=None):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)

            output = stdout.read().decode('utf-8')

            if write_to_path is not None:
                with open(write_to_path, 'w', encoding='utf-8') as f:
                    f.write(output)
            
            return output
        except Exception as e:
            print(f"An error occurred while executing ssh command: {command} : {e}")
