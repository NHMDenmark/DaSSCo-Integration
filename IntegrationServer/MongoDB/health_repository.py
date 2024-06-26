import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from datetime import datetime, timedelta
import utility
from MongoDB import mongo_connection, all_repository
from Enums.status_enum import Status

class HealthRepository(Status):

    def __init__(self):
        Status.__init__(self)
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
    
    def create_health_entry_from_api(self, id, data):
            self.collection.insert_one({"_id": id, **data})

    # TODO logic
    def get_count_errors(self, minutes, service):
        pass
    # TODO logic
    def get_count_warnings(self, minutes, service):
        pass
    
    def get_recent_errors(self, service_name, interval, severity_level = "ERROR"):
    
    
        time_ago = datetime.now() - timedelta(minutes=interval)
        
        # Query to find entries with severity_level "ERROR", specific service name, and time ago
        query = {
            'severity_level': severity_level,
            'service': service_name,
            'timestamp': {'$gte': time_ago.strftime("%Y-%m-%d %H:%M:%S,%f")}
        }
        
        # Fetch the entries
        results = list(self.collection.find(query))
        
        return results

            