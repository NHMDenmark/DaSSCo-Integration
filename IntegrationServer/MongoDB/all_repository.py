import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
import datetime

class AllRepository:

    def __init__(self, collection):
        self.util = utility.Utility()
        self.collection = collection

    def update_entry(self, guid, key, value):
        """
            Update or add to an entry in the MongoDB collection.

            :param guid: The unique identifier of the entry.
            :param key: The key (field) to be updated or created.
            :param value: The new value for the specified key.
            :return: A boolean denoting success or failure.
        """
        if self.get_entry("_id", guid) is None:
            return False

        query = {"_id": guid}
        update_data = {"$set": {key: value}}

        self.collection.update_one(query, update_data)

        return True
    
    def get_entry(self, key, value):
        """
                Retrieve an entry from the MongoDB collection based on a key value pair.
                :param key: Key. Could be _id
                :param value: Value. Could be our "guid"
                :return: The first entry matching the specified pair. Returns None if nothing matches.
                """
        query = {key: value}
        entry = self.collection.find_one(query)
        return entry
    
    def get_entries(self, key, value):
        """
        Retrieve entries from the MongoDB collection based on a key value pair.

        :param key: Key to be found.
        :param value: Value to be found. 
        :return: A list of entries matching the specified pair. Returns an empty list if nothing matches.
        """
        query = {key: value}
        entries = list(self.collection.find(query))
        return entries

    def get_all_entries_in_db(self):
        """
        Retrieve all entries in a mongo db

        :return: A list of entries, returns an empty list if nothing is there
        """
        entries = list(self.collection.find())

        return entries

    def get_entry_from_multiple_key_pairs(self, key_value_pairs):
        """
            Retrieve an entry from the MongoDB collection based on multiple key-value pairs. [{key: value, key: value}]

            :param key_value_pairs: List of dictionaries representing key-value pairs.
            :return: The first entry matching the specified pair. Returns None if nothing matches.
            """
        query = {"$and": key_value_pairs}
        entry = self.collection.find_one(query)
        return entry
    
    def get_entries_from_multiple_key_pairs(self, key_value_pairs):
        """
        Retrieve entries from the MongoDB collection based on multiple key-value pairs. [{key: value, key: value}]

        :param key_value_pairs: List of dictionaries representing key-value pairs.
        :return: A list of entries matching the specified pairs. Returns an empty list if nothing matches.
        """
        query = {"$and": key_value_pairs}
        entries = list(self.collection.find(query))
        return entries

    def get_time_based_multiple_key(self, key_value_pairs, time_key = None, after = None, before = None):

        if time_key is not None:
            
            time_query = {time_key: {}}

            if after is not None:
            # Convert "after" into a datetime if it isn't one already.
                if not isinstance(after, datetime.datetime):
                    after = datetime.datetime(after)
                time_query[time_key].update({"$gte": after})
        
            if before is not None:
                if not isinstance(before, datetime.datetime):
                    before = datetime.datetime(before)
                time_query[time_key].update({"$lte": before})

            key_value_pairs.append(time_query)

        query = {"$and": key_value_pairs}
        
        entries = list(self.collection.find(query))
        return entries

    def insert_entry(self, id, data):
        """
            Insert any document based on a dictionary.

            :param id: The id of the new entry
            :param data: The dictionary with the data for the document
            :return: True for success, False for failure.
        """
        try:
            self.collection.insert_one({"_id": id, **data})
            return True
        except Exception as e:
            print(e)
            return False

    def get_value_for_key(self, id_value, key):
        """
            Retrieve a single value from the MongoDB collection based on an _id and a key.

            :param id_value: The _id value.
            :param key: The key for which to retrieve the value.
            :return: The value corresponding to the specified key.
        """    
        query = {"_id": id_value}
        entry = self.collection.find_one(query)

        if entry and key in entry:
            return entry[key]
        else:
            return None
    

    def delete_entry(self, guid):
        """
                Delete an entry from the MongoDB collection based on its unique identifier.

                :param guid: The unique identifier of the entry.
                :return: A boolean denoting success or failure.
        """

        if self.get_entry("_id", guid) is None:
            return False

        query = {"_id": guid}
        self.collection.delete_one(query)

        return True
    
    def append_existing_list(self, guid, list_key, value):
        """
                Appends an existing list in an entry with a value.

                :param guid: The unique identifier of the entry.
                :param list_key: The key identifier of the list.
                :param value: The value to be appended to the list.
                :return: A boolean denoting success or failure.
        """
        entry = self.get_entry("_id", guid)

        if entry is None:
            return False
        
        if list_key not in entry:
            return False

        entry[list_key].append(value)

        self.collection.update_one({"_id": guid}, {"$set": entry})

        return True
    
    def delete_field(self, id, field_name):
        """
        Delete a specific field from an entry in the MongoDB collection based on its unique identifier.

        :param guid: The unique identifier of the entry.
        :param field_name: The name of the field to delete.
        :return: A boolean denoting success or failure.
        """

        if self.get_entry("_id", id) is None:
            return False

        query = {"_id": id}
        update = {"$unset": {field_name: ""}}
        result = self.collection.update_one(query, update)

        return result.modified_count > 0
    
    def calculate_values_for_fields_with_key_value(self, field, key, value):
        """
        Retrieve entries from the MongoDB collection based a key and a value.
        Calculate the sum of a field from those entries. 
        :param key: The key
        :param value: The value
        :param field: The field to be calculated
        :return: A total of the field for the entries found, 0 if not entries found or False.
        """        
        try:
            query = {key:value}
            entries = list(self.collection.find(query))

            total = 0
            for entry in entries:
                total = total + entry[field]
            
            return total
        except Exception as e:
            print(e)
            return False
        
    def multiple_key_values_calculate_field_total_value(self, field, key_value_pairs):
        """
        Retrieve entries from the MongoDB collection based on multiple key-value pairs. [{key: value, key: value}]
        Calculate the sum of a field from those entries. 
        :param key_value_pairs: List of dictionaries representing key-value pairs.
        :param field: The field to be calculated
        :return: A total of the field for the entries found, 0 if not entries found or False.
        """
        try:
            query = {"$and": key_value_pairs}
            entries = list(self.collection.find(query))
            
            total = 0
            for entry in entries:
                total = total + entry[field]
                
            return total
            
        except Exception as e:
            print(e)
            return False
    
    def get_count_for_key_value_pair(self, key, value):
        """
        Retrieve entries from the MongoDB collection based a key and a value.
        Counts the amount of entries found. 
        :param key: The key
        :param value: The value
        :return: The number of entries found, 0 if not entries found or False.
        """
        try:
            query = {key:value}
            entries = list(self.collection.find(query))

            total = 0
            for entry in entries:
                total = total + 1
            
            return total
        
        except Exception as e:
            print(e)
            return False