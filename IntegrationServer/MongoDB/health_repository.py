import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from MongoDB import mongo_connection, all_repository

class HealthRepository:

    def __init__(self):
        self.util = utility.Utility()
        self.mongo_health = mongo_connection.MongoConnection("health")

        self.collection = self.mongo_health.get_collection()
        self.all = all_repository.AllRepository(self.collection)

    def close_connection(self):
        self.mongo_health.close_mdb()

    def update_entry(self, id, key, value):
        return self.all.update_entry(id, key, value)

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

    def delete_entry(self, id):
        return self.all.delete_entry(id)
    
    def create_health_entry_from_api(self, data):
            self.collection.insert_one({**data})

    # TODO logic
    def get_count_errors(self, minutes, service):
        pass
    # TODO logic
    def get_count_warnings(self, minutes, service):
        pass
    


            