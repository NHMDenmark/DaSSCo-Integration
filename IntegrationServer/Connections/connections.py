import os

from IntegrationServer.Connections.ssh import SSHConnection
from IntegrationServer.utility import Utility


class Connections:
    def __init__(self):
        self.connections = []
        self.util = Utility()

    def create_ssh_connections(self, ssh_file_path):
        config = self.util.read_json(ssh_file_path)

        for connection_name, connection_details in config.items():
            con_user = connection_name + "_USER"
            con_user.upper()
            con_pwd = connection_name + "_PWD"
            con_pwd.upper()

            username = os.getenv(con_user)
            password = os.getenv(con_pwd)

            connection = SSHConnection(
                connection_name,
                connection_details['host'],
                connection_details['port'],
                username,
                password
            )
            updated_connection = self.util.get_value(ssh_file_path, connection_name)
            connection.__setattr__("status", updated_connection.get("status"))
            connection.__setattr__("new_import_directory_path", updated_connection.get("new_import_directory_path"))
            connection.__setattr__("updated_import_directory_path", updated_connection.get("updated_import_directory_path"))
            connection.__setattr__("export_directory_path", updated_connection.get("export_directory_path"))
            connection.__setattr__("is_slurm", updated_connection.get("is_slurm"))

            if updated_connection.get("status") == "open":
                self.connections.append(connection)

    def close_all(self):
        for con in self.connections:
            con.close()
        self.connections = []

    def get_connections(self):
        return self.connections
