import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from MongoDB import mongo_connection, all_repository
from pymongo.errors import InvalidOperation
from Enums.asset_type_enum import AssetTypeEnum

class SshConnectionRepository:

    def __init__(self):
        self.util = utility.Utility()
        self.mongo_ssh = mongo_connection.MongoConnection("ssh")

        self.collection = self.mongo_ssh.get_collection()
        self.all = all_repository.AllRepository(self.collection)


    def close_connection(self):
        self.mongo_ssh.close_mdb()

    """
    Returns true if there is no issue, else returns the exception.
    """
    def check_connection(self):
        try:
            reply = self.mongo_ssh.ping_connection()
        except InvalidOperation as e:
            return e
        return reply

    def update_entry(self, guid: str, key, value):
        return self.all.update_entry(guid, key, value)

    def get_entry(self, key, value):
        return self.all.get_entry(key, value)
    
    def get_all_entries(self):
        return self.all.get_all_entries_in_db()
    
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
    
    def delete_field(self, id, field_name):
        return self.all.delete_field(id, field_name)
    
    def insert_default_value(self, config):
        """
        Inserts a new document with the given _id.
        If the document with that _id already exists, it won't insert a duplicate.
        """
        try:
            # Insert the document with _id and value if it doesn't exist
            self.collection.insert_one({"_id": config, "status": "closed", "pid": None})
            return True
        except Exception as e:
            print(f"An error occurred while inserting: {e}")
            return False