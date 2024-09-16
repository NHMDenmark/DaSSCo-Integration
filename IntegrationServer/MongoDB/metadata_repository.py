import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from MongoDB import mongo_connection, all_repository
from pymongo.errors import InvalidOperation

class MetadataRepository:

    def __init__(self):
        self.util = utility.Utility()
        self.mongo_metadata = mongo_connection.MongoConnection("metadata")

        self.collection = self.mongo_metadata.get_collection()
        self.all = all_repository.AllRepository(self.collection)

    def close_connection(self):
        self.mongo_metadata.close_mdb()
    
    """
    Returns true if there is no issue, else returns the exception.
    """
    def check_connection(self):
        try:
            reply = self.mongo_metadata.ping_connection()
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

    def create_metadata_entry(self, json_path, guid):
        """
        Create a new metadata entry in the MongoDB collection.
        :param json_path: The path to the metadata file.
        :param guid: The unique identifier of the entry.
        :return: A boolean denoting success or failure.
        """        
        data = self.util.read_json(json_path)

        if data is False:
            return False        

        if self.get_entry("_id", guid) is None:

            self.collection.insert_one({"_id": guid, **data})
            
            return True
        
        return False

    # TODO missing unit test
    def create_metadata_entry_from_api(self, guid, data):
        
        if self.get_entry("_id", guid) is None:
            
            self.collection.insert_one({"_id": guid, **data})
            return True
        else:
            print("returning false")
            return False
