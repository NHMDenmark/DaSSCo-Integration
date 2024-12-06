import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from datetime import datetime, timedelta

import utility
from MongoDB import mongo_connection, all_repository
from pymongo.errors import InvalidOperation
from Enums.asset_type_enum import AssetTypeEnum

class ThrottleRepository:

    def __init__(self):
        self.util = utility.Utility()
        self.mongo_throttle = mongo_connection.MongoConnection("throttle")

        self.collection = self.mongo_throttle.get_collection()
        self.all = all_repository.AllRepository(self.collection)


    def close_connection(self):
        self.mongo_throttle.close_mdb()

    """
    Returns true if there is no issue, else returns the exception.
    """
    def check_connection(self):
        try:
            reply = self.mongo_throttle.ping_connection()
        except InvalidOperation as e:
            return e
        return reply

    def update_entry(self, guid: str, key, value):
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
    
    def delete_field(self, id, field_name):
        return self.all.delete_field(id, field_name)

    def insert_default_value(self, config):
        """
        Inserts a new document with the given _id and a default value of 0 for 'value'.
        If the document with that _id already exists, it won't insert a duplicate.
        """
        try:
            # Insert the document with _id and value if it doesn't exist
            self.collection.insert_one({"_id": config, "value": 0})
            return True
        except Exception as e:
            print(f"An error occurred while inserting: {e}")
            return False

    def add_one_to_count(self, _id, key):
        """
        Increments the value of the given key in the document with the specified _id by 1.
        """
        try:
            self.collection.update_one(
                {"_id": _id},       # Find the document by _id
                {"$inc": {key: 1}}     # Increment the value of the specified key by 1
            )
            return True            
        except Exception as e:
            return False

    def subtract_one_from_count(self, _id, key):
        """
        Decreases the value of the given key in the document with the specified _id by 1.
        """
        try:
            self.collection.update_one(
                {"_id": _id},       # Find the document by _id
                {"$inc": {key: -1}}     # Decreases the value of the specified key by 1
            )
            return True            
        except Exception as e:
            return False

    def add_to_amount(self, _id, key, amount):
        """
        Increments the value of the given key in the document with the specified _id by specified amount.
        """
        try:
            self.collection.update_one(
                {"_id": _id},       # Find the document by _id
                {"$inc": {key: amount}}     # change the value of the specified key
            )
            return True            
        except Exception as e:
            return False

    def subtract_from_amount(self, _id, key, amount):
        """
        Decreases the value of the given key in the document with the specified _id by specified amount.
        """
        try:
            self.collection.update_one(
                {"_id": _id},       # Find the document by _id
                {"$inc": {key: -amount}}     # change the value of the specified key
            )
            return True            
        except Exception as e:
            return False
    
    def reset_throttle(self):
        try:
            self.all.update_entry("max_assets_in_flight", "value", 0)
            self.all.update_entry("max_sync_asset_count", "value", 0)
            self.all.update_entry("total_max_asset_size_mb", "value", 0)
            self.all.update_entry("total_max_new_asset_size_mb", "value", 0)
            self.all.update_entry("total_max_derivative_size_mb", "value", 0)
            self.all.update_entry("total_reopened_share_size_mb", "value", 0)
            return True
        except Exception as e:
            return False