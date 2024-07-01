import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from MongoDB import mongo_connection, all_repository
from MongoDB.service_model import ModelService
from Enums.status_enum import Status
from pymongo.errors import InvalidOperation

class ServiceRepository(Status):

    def __init__(self):
        super().__init__()
        self.util = utility.Utility()
        self.mongo_micro_service = mongo_connection.MongoConnection("micro_service")

        self.collection = self.mongo_micro_service.get_collection()
        self.all = all_repository.AllRepository(self.collection)
        
    def create_micro_service_entry(self, name):
        """
        Create a new mos entry in the MongoDB collection.
        :param name: The unique identifier of the entry.
        
        :return: A boolean denoting success or failure.
        """  
    
        if self.get_entry("_id", name) is None:

            model_service = ModelService()
            entry = model_service.create_model(name)

            self.collection.insert_one(entry)
            return True
        else:
            return False
    
    def close_connection(self):
        self.mongo_micro_service.close_mdb()
    
    """
    Returns true if there is no issue, else returns the exception.
    """
    def check_connection(self):
        try:
            reply = self.mongo_micro_service.ping_connection()
        except InvalidOperation as e:
            return e
        return reply

    def update_entry(self, service_name: str, key, value):
        return self.all.update_entry(service_name, key, value)

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

    def delete_entry(self, name):
        return self.all.delete_entry(name)
    
    def append_existing_list(self, name, list_key, value):
        return self.all.append_existing_list(name, list_key, value)