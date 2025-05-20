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

    def insert_entry(self, id, data):
        return self.all.insert_entry(id, data)

    def delete_entry(self, guid):
        return self.all.delete_entry(guid)
    
    def append_existing_list(self, guid, list_key, value):
        return self.all.append_existing_list(guid, list_key, value)

    def get_time_based_multiple_key_list(self, key_value_pairs, time_key=None, after=None, before=None):

        return self.all.get_time_based_multiple_key(key_value_pairs, time_key=time_key, after=after, before=before)

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
        
    def get_issue_from_key_value(self, guid, key, value):
        """
                Finds an issue based on the asset and a key value pair of the issue.
                :returns the issue info or none
        """

        issue_key = f"issues.{key}"

        result = self.collection.find_one({ "_id": guid, issue_key: value },{ "issues.$": 1 })
        
        # get the actual job info from the resulting dictionary
        if result and "issues" in result:
            result = result["issues"][0]
            return result
        
        return None
    
    def get_issue_from_key_value_pairs(self, guid, key_value_pairs):
        """
        Finds an issue in the 'issues' array of a document with the given guid, matching all key-value pairs.

        :param guid: The asset _id (GUID).
        :param key_value_pairs: Dictionary of key-value pairs to match inside an issue.
        :return: The first matching issue or None.
        """
        # Build query using $elemMatch for nested matching
        issue_query = {
            "_id": guid,
            "issues": {"$elemMatch": key_value_pairs}
        }

        # Use projection to return only the matched issue
        result = self.collection.find_one(issue_query, {"issues.$": 1})

        if result and "issues" in result:
            return result["issues"][0]

        return None

    def update_issue_data(self, guid, key_value_pairs_identify, key_value_pairs_to_update):
        """
        Update an issue's fields inside the 'issues' array of a document, based on matching key-value pairs.

        :param guid: The asset _id (GUID).
        :param key_value_pairs_identify: Dictionary of key-value pairs to identify the issue.
        :param key_value_pairs_to_update: Dictionary of key-value pairs to update in the matched issue.
        :return: True if a document was modified, False otherwise.
        """
        # Prepare the array filter with identifier keys
        array_filter = {f"issue.{k}": v for k, v in key_value_pairs_identify.items()}

        # Prepare the update keys with positional $[issue]
        update_fields = {f"issues.$[issue].{k}": v for k, v in key_value_pairs_to_update.items()}

        result = self.collection.update_one(
            {"_id": guid},
            {"$set": update_fields},
            array_filters=[array_filter]
        )

        return result.modified_count > 0 