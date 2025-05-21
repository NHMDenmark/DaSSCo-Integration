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
variables. Where NAME is the connection name set in the config file.
Includes functions for creating, getting and shutting down connection(s).  
"""
class Connections:
    def __init__(self):
        load_dotenv()
        self.util = Utility()
        self.ssh_config_path = f"{project_root}/ConfigFiles/ssh_connections_config.json" 
        self.connection = None
        self.msg = None
        self.exc = None
    """
    Creates a ssh connection. Retrieves the information for the
    connection from a ssh_connections_config.json file.
    Takes the name of the connection as parameter. 
    """
    def create_ssh_connection(self, ssh_name):
        config = self.util.get_value(self.ssh_config_path, ssh_name)
        
        con_user = ssh_name + "_USER"
        con_user = con_user.upper()
        con_pwd = ssh_name + "_PWD"
        con_pwd = con_pwd.upper()
            
        username = os.getenv(con_user)
        password = os.getenv(con_pwd)

        if username == None:
            username = os.environ.get(con_user)
        print("attempt: ", username, ssh_name)
        try:
            connection = SSHConnection(
                ssh_name,
                config['host'],
                config['port'],
                username,
                password
                )
                
            test_connection = True

        except Exception as e:
            self.exc = e
            self.msg = "Failed to establish the ssh connection."

        if test_connection:
            self.connection = connection        

    def create_ssh_connection_by_name(self, connection_name):

        connections_config_details = self.util.read_json(self.ssh_config_path)
        
        connection_details = connections_config_details[connection_name]
        print(connection_details["host"])
        con_user = connection_name + "_USER"
        con_user = con_user.upper()
        
        username = os.getenv(con_user)
        
        if username == None:
            username = os.environ.get(con_user)
        password = None

        connection = None
        try:
            connection = SSHConnection(
                    connection_name,
                    connection_details["host"],
                    connection_details["port"],
                    username,
                    password
                )
        except Exception as e:
            print(e)
        
        if connection is not None:
            self.connection = connection


    def close_connection(self):
        if self.connection is not None:
            self.connection.close()

    def get_connection(self):
        return self.connection
