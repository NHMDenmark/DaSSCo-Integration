import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from Connections.ssh import SSHConnection
from utility import Utility
from dotenv import load_dotenv

"""
Creates ssh connections from a _connection_config.json file.
Connection username and connection passwords must be called {NAME}_USER and {NAME}_PWD in the environment
variables.
Includes functions for creating, getting and shutting down connection(s).  
"""


class Connections:
    def __init__(self):
        load_dotenv()
        self.util = Utility()
        self.connection = None
        self.msg = None
        self.exc = None
    """
    Creates a ssh connection and sets a number of attributes for that connection. Retrieves the information for the
    connection from a xxx_connection_config.json file. 
    """
    def create_ssh_connection(self, ssh_file_path):
        config = self.util.read_json(ssh_file_path)
        self.msg = None
        self.exc = None

        for connection_name, connection_details in config.items():
            con_user = connection_name + "_USER"
            con_user = con_user.upper()
            con_pwd = connection_name + "_PWD"
            con_pwd = con_pwd.upper()
            
            username = os.getenv(con_user)
            password = os.getenv(con_pwd)

            if username == None:
                username = os.environ.get(con_user)
            print("attempt: ", username, connection_name)
            connection = SSHConnection(
                connection_name,
                connection_details['host'],
                connection_details['port'],
                username,
                password
            )
            updated_connection = self.util.get_value(ssh_file_path, connection_name)
            connection.__setattr__("status", updated_connection.get("status"))
            connection.__setattr__("export_directory_path", updated_connection.get("export_directory_path"))
            connection.__setattr__("is_slurm", updated_connection.get("is_slurm"))

            if updated_connection.get("status") == "open":
                self.connection = connection
            else:
                self.msg = connection.msg
                self.exc = connection.exc

    def close_connection(self):
        if self.connection is not None:
            self.connection.close()

    def get_connection(self):
        return self.connection
