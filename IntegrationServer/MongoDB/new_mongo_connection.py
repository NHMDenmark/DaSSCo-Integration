import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from datetime import datetime, timedelta

from pymongo import MongoClient
from bson import ObjectId
import utility

from MongoDB import entry_model

"""
Class for connecting to and interacting with a MongoDB. Takes the name of the database as argument in constructor.
We use this to keep track of jobs and their status for each asset. 
Should have full CRUD available. 
"""


# TODO ensure full crud functionalities have been added.
# TODO integrate with old system for keeping track of jobs through _jobs.json

class MongoConnection:

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
        self.client.close()
        print(f"closed connection to: {self.name}")

    # TODO figure out if this is still in use and if so can it be moved
    def add_entry_to_list(self, guid, list_name):
        """
                Adds an assets guid to a list. Used to keep track of which batch assets belong to.

                :param guid: The unique identifier of the entry.
                :param list_name: The unique identifier of the list.
                :return: A boolean denoting success or failure. This cant fail unless there is no connection to a database. 
        """
        entry = self.get_entry("_id", list_name)

        if entry is None:
            # If the list doesn't exist, create a new entry with a list containing the guid
            self.collection.insert_one({"_id": list_name, "guids": [guid]})
        else:
            # If the list already exists, append the guid to the existing list
            self.collection.update_one({"_id": list_name}, {"$push": {"guids": guid}})

        return True