import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from datetime import datetime, timedelta

from pymongo import MongoClient
from bson import ObjectId
import utility
from MongoDB import track_model
from pymongo.errors import ConnectionFailure

"""
Class for connecting to and interacting with a MongoDB. Takes the name of the database as argument in constructor.
We use this to keep track of jobs and their status for each asset. 
Should have full CRUD available. 
"""
# TODO ensure full crud functionalities have been added.

class MongoConnection:

    def __init__(self, name):
        self.util = utility.Utility()
        self.name = name

        # Needs to use absolute path here for api to work
        self.slurm_config_path = f"{project_root}/ConfigFiles/slurm_config.json"

        self.mongo_config_path = f"{project_root}/ConfigFiles/mongo_connection_config.json"
        self.config_values = self.util.get_value(self.mongo_config_path, self.name)

        self.host = self.config_values.get("host")
        self.port = self.config_values.get("port")
        self.data_base = self.config_values.get("data_base")
        self.collection_name = self.config_values.get("collection_name")

        # Connect to the MongoDB server
        self.client = MongoClient(self.host, self.port)  # Default MongoDB server address and port

        # Access a specific database (create it if it doesn't exist)
        self.mdb = self.client[self.data_base]

        # Access a specific collection within the database (create it if it doesn't exist)
        self.collection = self.mdb[self.collection_name]
        print(f"connected to: {self.name}")
        
    def get_collection(self):
        return self.collection

    def close_mdb(self):
        self.client.close()
        print(f"closed connection to: {self.name}")
    
    """
    Checks the connection is alive. 
    """
    def ping_connection(self):
        try:
            self.client.admin.command("ping")            
        except ConnectionFailure as e:
            return e
        return True

    """
    TODO Everything below here isnt strictly needed in this file. At some point it should be deleted since all the methods
    have already been moved to either their respective repositories or to the all_repository.
    Deleting should not be done without being sure everything else has changed to using the new setup for repositories. This 
    includes tests.     
    """

    def create_track_entry(self, guid, pipeline):
        """
        Create a new track entry in the MongoDB collection.

        :param guid: The unique identifier of the asset.
        :param pipeline: The value for the 'pipeline' field.
        """
        model = track_model.EntryModel(guid, pipeline)
        entry_data = model.get_entry_data()

        if self.get_entry("_id", guid) is None:
            # Insert the new document into the collection
            self.collection.insert_one(entry_data)
            return True
        else:
            return False
    
    def create_derivative_track_entry(self, guid, pipeline):
        """
        Create a new track entry in the MongoDB collection for a derivative.

        :param guid: The unique identifier of the asset.
        :param pipeline: The value for the 'pipeline' field.
        :return: A boolean denoting success or failure.
        """
        model = track_model.EntryModel(guid, pipeline, derivative=True)
        entry_data = model.get_entry_data()

        if self.get_entry("_id", guid) is None:
            # Insert the new document into the collection
            self.collection.insert_one(entry_data)
            return True
        else:
            return False
    
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
        else:
            return False

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
    
    def update_track_job_status(self, guid, job, status):
        """
            Update an existing track_entry with a new status for a job in the MongoDB collection.

            :param guid: The unique identifier of the entry.
            :param job: The job name to be updated.
            :param status: The new status for the specified job.
            :return: A boolean denoting success or failure.
        """
        # Retrieve the entry
        entry = self.get_entry("_id", guid)
        if entry is None:
            return False

        # Check if the job exists in the job_list
        job_exists = any(d['name'] == job for d in entry.get('job_list', []))
        if not job_exists:
            return False

        self.collection.update_one({"_id": guid, "job_list.name": job}, {"$set": {"job_list.$.status": status}})

        return True
    
    def update_track_job_list(self, guid, job, key, value):
        """
            Update an existing track_entry with a new entry for a job in the MongoDB collection.

            :param guid: The unique identifier of the entry.
            :param job: The job name to be updated.
            :param key: The key (field) to be updated or created.
            :param value: The new value for the specified key.
            :return: A boolean denoting success or failure.
        """

        # Retrieve the entry
        entry = self.get_entry("_id", guid)
        if entry is None:
            return False

        # Check if the job exists in the job_list
        job_exists = any(d['name'] == job for d in entry.get('job_list', []))
        if not job_exists:
            return False

        query = {"_id": guid, "job_list.name": job}
        job_entry = f"job_list.$.{key}"
        update_data = {"$set": {job_entry: value}}

        self.collection.update_one(query, update_data)

        return True

    def update_track_file_list(self, guid, file, key, value):
        """
            Update an existing track_entry with a new entry for a file in the track MongoDB collection.

            :param guid: The unique identifier of the entry.
            :param file: The file name to be updated.
            :param key: The key (field) to be updated or created.
            :param value: The new value for the specified key.
            :return: A boolean denoting success or failure.
        """

        # Retrieve the entry
        entry = self.get_entry("_id", guid)
        if entry is None:
            return False

        # Check if the file exists in the file_list
        file_exists = any(d['name'] == file for d in entry.get('file_list', []))
        if not file_exists:
            return False

        query = {"_id": guid, "file_list.name": file}
        file_entry = f"file_list.$.{key}"
        update_data = {"$set": {file_entry: value}}

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
    
    def add_entry_to_list(self, guid, list_name):
        """
                Adds an assets guid to a list. Used to keep track of which batch assets belong to.

                :param guid: The unique identifier of the entry.
                :param list_name: The unique identifier of the list.
                :return: A boolean denoting success or failure. This cant fail unless there is no connection to a database. 
        """
        entry = self.get_entry("_id", list_name)

        if entry is None:
            # If the list doesn't exist, create a new entry with a list containing the guid
            self.collection.insert_one({"_id": list_name, "guids": [guid]})
        else:
            # If the list already exists, append the guid to the existing list
            self.collection.update_one({"_id": list_name}, {"$push": {"guids": guid}})

        return True
     
    # This can probably be made easier by just finding jobs that are running and getting the time stamps for those. Will depend on implementation in app script.
    # TODO missing unit test
    def find_running_jobs_older_than(self):
        """
                Finds an entry based on its job_start_time compared to current time and the max time set in the config file. 

                :return the first entry with a timestamp too old
        """
        max_time = self.util.get_value(self.slurm_config_path, "max_expected_time_running_job")
        
        time_ago = datetime.now() - timedelta(hours=max_time)

        result = self.collection.find({"job_list.job_start_time": {"$lt": time_ago}})
        
        return result
    
    # This can probably be made easier by just finding jobs that are running and getting the time stamps for those. Will depend on implementation in app script.
    # TODO missing unit test
    def find_queued_jobs_older_than(self):
        """
                Finds an entry based on its job_queued_time compared to current time and the max time set in the config file. 

                :return the first entry with a timestamp too old
        """
        max_time = self.util.get_value(self.slurm_config_path, "max_expected_time_in_queue")
        
        time_ago = datetime.now() - timedelta(hours=max_time)

        result = self.collection.find({"job_list.job_queued_time": {"$lt": time_ago}})
        
        return result
    
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