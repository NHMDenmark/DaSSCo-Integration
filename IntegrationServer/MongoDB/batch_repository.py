import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from MongoDB import mongo_connection, all_repository
from pymongo.errors import InvalidOperation

class BatchRepository:

    def __init__(self):
        self.util = utility.Utility()
        self.mongo_batch = mongo_connection.MongoConnection("batch")

        self.collection = self.mongo_batch.get_collection()
        self.all = all_repository.AllRepository(self.collection)

    def close_connection(self):
        self.mongo_batch.close_mdb()

    """
    Returns true if there is no issue, else returns the exception.
    """
    def check_connection(self):
        try:
            reply = self.mongo_batch.ping_connection()
        except InvalidOperation as e:
            return e
        return reply

    def update_entry(self, guid, key, value):
        return self.all.update_entry(guid, key, value)

    def get_entry(self, key, value):
        return self.all.get_entry(key, value)
    
    def get_entries(self, key, value):
        return self.all.get_entries(key, value)

    def get_entry_from_multiple_key_pairs(self, key_value_pairs):
        return self.all.get_entry_from_multiple_key_pairs(key_value_pairs)
    
    def get_entries_from_multiple_key_pairs(self, key_value_pairs):
        return self.all.get_entries_from_multiple_key_pairs(key_value_pairs)

    def get_value_for_key(self, id_value, key):
        return self.all.get_value_for_key(id_value, key)

    def delete_entry(self, guid):
        return self.all.delete_entry(guid)
    
    def append_existing_list(self, guid, list_key, value):
        return self.all.append_existing_list(guid, list_key, value)
    
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