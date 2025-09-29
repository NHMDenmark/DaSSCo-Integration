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
        
        # handle that issues should be appended to an existing list
        if key != "issues":
            update_data = {"$set": {key: value}}            
        else:
            update_data = {"$push": {key: {"$each": value}}}
            
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
    
    def get_entry_key_exist_and_key_pair_values(self, key_value_pairs, must_have_key=None):
        """
        Retrieve an entry from the MongoDB collection based on multiple key-value pairs,
        and optionally ensure a specific key exists in the entry.

        :param key_value_pairs: List of dictionaries representing key-value pairs. E.g., [{"a": 1}, {"b": 2}]
        :param must_have_key: Optional; a key that must exist in the matched document.
        :return: The first entry matching the specified criteria. Returns None if nothing matches.
        """
        query_conditions = key_value_pairs.copy()  # ensure we don't mutate input

        if must_have_key:
            query_conditions.append({must_have_key: {"$exists": True}})

        query = {"$and": query_conditions} if query_conditions else {}
        return self.collection.find_one(query)
    
    def get_entries_from_multiple_key_pairs(self, key_value_pairs):
        """
        Retrieve entries from the MongoDB collection based on multiple key-value pairs. [{key: value, key: value}]

        :param key_value_pairs: List of dictionaries representing key-value pairs.
        :return: A list of entries matching the specified pairs. Returns an empty list if nothing matches.
        """
        query = {"$and": key_value_pairs}
        entries = list(self.collection.find(query))
        return entries

    def get_time_based_multiple_key(self, key_value_pairs, time_key=None, after=None, before=None):
        
        kvp = list(key_value_pairs)  # copy so we don’t mutate caller’s list

        # --- detect field type ---
        sample_doc = self.collection.find_one({time_key: {"$exists": True}}, {time_key: 1})
        field_is_datetime = False
        if sample_doc and isinstance(sample_doc.get(time_key), datetime.datetime):
            field_is_datetime = True

        # --- build query depending on type ---
        if time_key is not None:
            time_query = {time_key: {}}

            if after is not None:
                if field_is_datetime:
                    # ensure proper datetime
                    if not isinstance(after, datetime.datetime):
                        after = datetime.datetime.fromisoformat(str(after))
                    time_query[time_key].update({"$gte": after})
                else:
                    # ensure string in ISO8601 format
                    if isinstance(after, datetime.datetime):
                        after = after.strftime("%Y-%m-%dT%H:%M:%S+00:00")
                    time_query[time_key].update({"$gte": after})

            if before is not None:
                if field_is_datetime:
                    if not isinstance(before, datetime.datetime):
                        before = datetime.datetime.fromisoformat(str(before))
                    time_query[time_key].update({"$lte": before})
                else:
                    if isinstance(before, datetime.datetime):
                        before = before.strftime("%Y-%m-%dT%H:%M:%S+00:00")
                    time_query[time_key].update({"$lte": before})

            kvp.append(time_query)

        query = {"$and": kvp}

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
        
    def get_entries_with_value_less_than(self, key, value):
        """
        Retrieve entries from the MongoDB collection where the given key's value
        is less than the provided value.

        :param key: The key (field name in the MongoDB documents)
        :param value: The threshold value
        :return: List of matching entries, or [] if none found, or False if error
        """
        try:
            query = {key: {"$lt": value}}
            entries = list(self.collection.find(query))
            return entries

        except Exception as e:
            print(f"Error in get_entries_with_value_less_than: {e}")
            return False
        
    def get_entries_with_values_between(self, key, min_value, max_value):
        """
        Retrieve entries from the MongoDB collection where the given key's value
        is between min_value and max_value (inclusive).

        :param key: The key (field name in the MongoDB documents)
        :param min_value: The lower bound
        :param max_value: The upper bound
        :return: List of matching entries, or [] if none found, or False if error
        """
        try:
            query = {key: {"$gte": min_value, "$lte": max_value}}
            entries = list(self.collection.find(query))
            return entries

        except Exception as e:
            print(f"Error in get_entries_with_values_between: {e}")
            return False
