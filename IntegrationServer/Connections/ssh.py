import paramiko
import os
import stat
import time
from IntegrationServer.utility import Utility


class SSHConnection:
    def __init__(self, name, host, port, username, password):
        self.util = Utility()
        self.sftp = None
        self.name = name
        self.host = host
        self.port = port
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

    def connect(self):
        # need if statement, checking status for open already -  get specific value from json

        try:
            self.ssh_client.connect(self.host, self.port, self.username, self.password)
            print(f"connected to {self.name}")

            self.util.update_layered_json("./ConfigFiles/ucloud_connection_config.json", [self.name, "status"], "open")
            self.sftp = self.get_sftp()

        except Exception as e:
            print(f"Connection failed: {e}")

    def close(self):
        try:
            self.sftp.close()
            self.ssh_client.close()
            self.util.update_layered_json("./ConfigFiles/ucloud_connection_config.json", [self.name, "status"], "closed")
            print(f"closed {self.name}")
        except Exception as e:
            print(f"There was no connection: {e}")

    def sftp_copy_file(self, path_to_copy_from, path_to_copy_to):
        try:
            self.sftp.put(path_to_copy_from, path_to_copy_to)
        except Exception as e:
            print(f"An error occurred: {e}")

    def import_and_sort_files(self, remote_folder, local_destination):

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

        except Exception as e:
            print(f"An error occurred: {e}")

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

    def sftp_check_files_are_transferred(self, local_path, remote_path):
        try:
            remote_files = self.sftp.listdir(remote_path)
            local_files = os.listdir(local_path)
        except Exception as e:
            print(f"Error: {e}")
            return

        remote_file_names = [os.path.basename(file) for file in remote_files]
        local_file_names = [os.path.basename(local_file) for local_file in local_files]

        # Check if local files exist on the remote server
        for local_name in local_file_names:
            if local_name not in remote_file_names:
                print(f"File {local_name} was not successfully transferred.")
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

    def ssh_command(self, command, write_to_path=None):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)

            # Print the output
            print("Command Output:")
            output = stdout.read().decode('utf-8')
            print(output)

            if write_to_path is not None:
                with open(write_to_path, 'w', encoding='utf-8') as f:
                    f.write(output)
            # Print any errors
            print("Command Errors:")
            print(stderr.read().decode('utf-8'))

        except Exception as e:
            print(f"An error occurred: {e}")
