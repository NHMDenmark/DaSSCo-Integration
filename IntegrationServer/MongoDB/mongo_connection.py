import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from datetime import datetime, timedelta

from pymongo import MongoClient
from bson import ObjectId
import utility
from MongoDB import track_model
from pymongo.errors import ConnectionFailure

class MongoConnection:
    """
    Class for connecting to and interacting with a MongoDB. Takes the name of the database as argument in constructor.
    """
    
    def __init__(self, name):
        self.util = utility.Utility()
        self.name = name

        # Needs to use absolute path here for api to work
        self.slurm_config_path = f"{project_root}/ConfigFiles/slurm_config.json"

        self.mongo_config_path = f"{project_root}/ConfigFiles/mongo_connection_config.json"
        self.config_values = self.util.get_value(self.mongo_config_path, self.name)

        self.host = self.config_values.get("host")
        self.port = self.config_values.get("port")
        self.data_base = self.config_values.get("data_base")
        self.collection_name = self.config_values.get("collection_name")

        # Connect to the MongoDB server
        self.client = MongoClient(self.host, self.port)  # Default MongoDB server address and port

        # Access a specific database (create it if it doesn't exist)
        self.mdb = self.client[self.data_base]

        # Access a specific collection within the database (create it if it doesn't exist)
        self.collection = self.mdb[self.collection_name]
        print(f"connected to: {self.name}")
        
    def get_collection(self):
        return self.collection

    def close_mdb(self):
        """Closes the connection to the database"""
        self.client.close()
        print(f"closed connection to: {self.name}")
    
    
    def ping_connection(self):
        """
        Checks the connection is alive. 
        """
        try:
            self.client.admin.command("ping")            
        except ConnectionFailure as e:
            return e
        return True