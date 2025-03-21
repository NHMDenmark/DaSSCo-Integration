import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from datetime import datetime, timedelta
import utility
from MongoDB import mongo_connection, all_repository
from Enums.status_enum import Status
from pymongo.errors import InvalidOperation

class HealthRepository(Status):

    def __init__(self):
        Status.__init__(self)
        self.util = utility.Utility()
        self.mongo_health = mongo_connection.MongoConnection("health")

        self.collection = self.mongo_health.get_collection()
        self.all = all_repository.AllRepository(self.collection)

    def close_connection(self):
        self.mongo_health.close_mdb()

    """
    Returns true if there is no issue, else returns the exception.
    """
    def check_connection(self):
        try:
            reply = self.mongo_health.ping_connection()
        except InvalidOperation as e:
            return e
        return reply
    
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
    
    def get_time_based_multiple_key_list(self, key_value_pairs, time_key=None, after=None, before=None):

        return self.all.get_time_based_multiple_key(key_value_pairs, time_key=time_key, after=after, before=before)

    def create_health_entry_from_api(self, id, data):
            self.collection.insert_one({"_id": id, **data})

    def insert_entry(self, id, data):
        return self.all.insert_entry(id, data)

    # TODO logic
    def get_count_errors(self, minutes, service):
        pass
    # TODO logic
    def get_count_warnings(self, minutes, service):
        pass
    
    def get_recent_errors(self, service_name, interval, severity_level = "ERROR"):
    
        time_ago = datetime.now() - timedelta(seconds=interval)
        
        # Query to find entries with severity_level "ERROR", specific service name, and time ago
        query = {
            'severity_level': severity_level,
            'service': service_name,
            'timestamp': {'$gte': time_ago.strftime("%Y-%m-%d %H:%M:%S,%f")}
        }
        
        # Fetch the entries
        results = list(self.collection.find(query))
        
        return results

            