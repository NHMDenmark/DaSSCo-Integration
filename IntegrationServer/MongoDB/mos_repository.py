import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from MongoDB import mongo_connection, all_repository

class MOSRepository:

    def __init__(self):
        self.util = utility.Utility()
        self.mongo_MOS = mongo_connection.MongoConnection("MOS")

        self.collection = self.mongo_MOS.get_collection()
        self.all = all_repository.AllRepository(self.collection)

    def close_connection(self):
        self.mongo_MOS.close_mdb()

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

    def create_mos_entry(self, guid, data):
        """
        Create a new mos entry in the MongoDB collection.
        :param guid: The unique identifier of the entry.
        :param data: The data for the entry.
        :return: A boolean denoting success or failure.
        """  

        if self.get_entry("_id", guid) is None:

            self.collection.insert_one({"_id": guid, **data})
            return True
        else:
            return False
