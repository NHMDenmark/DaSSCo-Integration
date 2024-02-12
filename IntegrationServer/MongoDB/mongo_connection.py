import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from datetime import datetime

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
        # self.mongo_config_path = "IntegrationServer/ConfigFiles/mongo_connection_config.json"
        # Needs to use absolute path here for api to work
        self.mongo_config_path = "C:/Users/tvs157/Desktop/VSC_projects/DaSSCo-Integration/IntegrationServer/ConfigFiles/mongo_connection_config.json"

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

    def create_track_entry(self, guid, pipeline):
        """
        Create a new track entry in the MongoDB collection.

        :param guid: The unique identifier of the asset.
        :param pipeline: The value for the 'pipeline' field.
        """
        model = entry_model.EntryModel(guid, pipeline)
        entry_data = model.get_entry_data()

        if self.get_entry("_id", guid) is None:
            # Insert the new document into the collection
            self.collection.insert_one(entry_data)
    
    def create_metadata_entry(self, json_path, guid):
        """
        Create a new metadata entry in the MongoDB collection.
        :param json_path: The path to the metadata file.
        :param guid: The unique identifier of the entry.
        """        
        data = self.util.read_json(json_path)        

        if self.get_entry("_id", guid) is None:

            self.collection.insert_one({"_id": guid, **data})


    def update_entry(self, guid, key, value):
        """
            Update an existing entry in the MongoDB collection.

            :param guid: The unique identifier of the entry.
            :param key: The key (field) to be updated or created.
            :param value: The new value for the specified key.
        """

        query = {"_id": guid}
        update_data = {"$set": {key: value}}

        self.collection.update_one(query, update_data)
    
    def update_track_job_status(self, guid, job, status):
        """
            Update an existing track_entry with a new status for a job in the MongoDB collection.

            :param guid: The unique identifier of the entry.
            :param job: The job name to be updated.
            :param status: The new status for the specified job.
        """
        self.collection.update_one({"_id": guid, "job_list.name": job}, {"$set": {"job_list.$.status": status}})

    def get_entry(self, key, value):
        """
                Retrieve an entry from the MongoDB collection based on a key value pair.

                :param key: Key. Could be _id
                :param value: Value. Could be our "guid"
                :return: The first entry matching the specified pair.
                """
        query = {key: value}
        entry = self.collection.find_one(query)
        return entry

    def get_value_for_key(self, id_value, key):
        """
            Retrieve a single value from the MongoDB collection based on an _id and a key.

            :param id_value: The _id value.
            :param key: The key for which to retrieve the value.
            :return: The value corresponding to the specified key.
            """
        query = {"_id": id_value}
        entry = self.collection.find_one(query)

        if entry and key in entry:
            return entry[key]
        else:
            return None

    def delete_entry(self, guid):
        """
                Delete an entry from the MongoDB collection based on its unique identifier.

                :param guid: The unique identifier of the entry.
                """
        query = {"_id": guid}
        self.collection.delete_one(query)
    
    def add_entry_to_batch_list(self, guid, batch_list_name):
        entry = self.get_entry("_id", batch_list_name)

        if entry is None:
            # If the batch list doesn't exist, create a new entry with a list containing the guid
            self.collection.insert_one({"_id": batch_list_name, "guids": [guid]})
        else:
            # If the batch list already exists, append the guid to the existing list
            self.collection.update_one({"_id": batch_list_name}, {"$push": {"guids": guid}})