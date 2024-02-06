from datetime import datetime

from pymongo import MongoClient
from bson import ObjectId
from utility import Utility

from MongoDB import job_model

"""
Class for connecting to and interacting with a MongoDB. Takes the name of the database as argument in constructor.
We use this to keep track of jobs and their status for each asset. 
Should have full CRUD available. 
"""


# TODO ensure full crud functionalities have been added.
# TODO integrate with old system for keeping track of jobs through _jobs.json

class MongoConnection:

    def __init__(self, name):
        self.util = Utility()
        self.name = name
        self.mongo_config_path = "IntegrationServer\ConfigFiles\mongo_connection_config.json"

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

    def create_entry(self, guid, pipeline):
        """
        Create a new entry in the MongoDB collection.

        :param guid: The unique identifier of the asset.
        :param pipeline: The value for the 'pipeline' field.
        """
        model = job_model.JobModel(guid, pipeline)
        entry_data = model.get_entry_data()

        if self.get_entry("_id", guid) is None:
            # Insert the new document into the collection
            self.collection.insert_one(entry_data)

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

    def delete_entry(self, guid):
        """
                Delete an entry from the MongoDB collection based on its unique identifier.

                :param guid: The unique identifier of the entry.
                """
        query = {"_id": guid}
        self.collection.delete_one(query)
