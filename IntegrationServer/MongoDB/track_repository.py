import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from datetime import datetime, timedelta

import utility
from MongoDB import mongo_connection, all_repository
from MongoDB import track_model
from pymongo.errors import InvalidOperation
from Enums.asset_type_enum import AssetTypeEnum

class TrackRepository:
    """
    Contains the track database functionalities.
    Includes the functions from the all repository.
    """
    def __init__(self):
        """Creates the connection object for track and all databases."""
        self.util = utility.Utility()
        self.mongo_track = mongo_connection.MongoConnection("track")

        self.collection = self.mongo_track.get_collection()
        self.all = all_repository.AllRepository(self.collection)

    def close_connection(self):
        """Closes the connection."""
        self.mongo_track.close_mdb()

    def check_connection(self):
        """
        Returns true if there is no issue, else returns the exception.
        """
        try:
            reply = self.mongo_track.ping_connection()
        except InvalidOperation as e:
            return e
        return reply

    def update_entry(self, guid: str, key, value):
        """
        Updates an entry in the repository with a new value for the specified key.

        :param guid: Unique identifier of the entry to be updated.
        :param key: The key in the entry whose value needs updating.
        :param value: The new value to set for the specified key.
        :return: The response from the underlying repository.
        """
        return self.all.update_entry(guid, key, value)

    def get_entry(self, key, value):
        """
        Retrieves a single entry from the repository that matches the given key-value pair.

        :param key: The key to search for.
        :param value: The value associated with the key to search for.
        :return: The matching entry from the repository, or None if not found.
        """
        return self.all.get_entry(key, value)

    
    def get_entries(self, key, value):
        """
        Retrieves all entries from the repository that match the given key-value pair.

        :param key: The key to search for.
        :param value: The value associated with the key to search for.
        :return: A list of matching entries from the repository.
        """
        return self.all.get_entries(key, value)


    def get_entry_from_multiple_key_pairs(self, key_value_pairs):
        """
        Retrieves a single entry that matches all the specified key-value pairs.

        :param key_value_pairs: A dictionary of key-value pairs to match.
        :return: The matching entry from the repository, or None if not found.
        """
        return self.all.get_entry_from_multiple_key_pairs(key_value_pairs)

    
    def get_entries_from_multiple_key_pairs(self, key_value_pairs):
        """
        Retrieves all entries that match the specified key-value pairs.

        :param key_value_pairs: A dictionary of key-value pairs to match.
        :return: A list of entries that match all the specified key-value pairs.
        """
        return self.all.get_entries_from_multiple_key_pairs(key_value_pairs)


    def get_value_for_key(self, id_value, key):
        """
        Retrieves the value of a specific key for the given identifier.

        :param id_value: The unique identifier of the entry.
        :param key: The key whose value needs to be retrieved.
        :return: The value associated with the specified key, or None if not found.
        """
        return self.all.get_value_for_key(id_value, key)


    def delete_entry(self, guid):
        """
        Deletes an entry from the repository.

        :param guid: Unique identifier of the entry to be deleted.
        :return: True if the deletion was successful, False otherwise.
        """
        return self.all.delete_entry(guid)

    
    def append_existing_list(self, guid, list_key, value):
        """
        Appends a value to an existing list in the specified entry.

        :param guid: Unique identifier of the entry to update.
        :param list_key: The key of the list to which the value will be appended.
        :param value: The value to append to the list.
        :return: True if the operation was successful, False otherwise.
        """
        return self.all.append_existing_list(guid, list_key, value)

    
    def delete_field(self, id, field_name):
        """
        Deletes a specific field from an entry in the repository.

        :param id: Unique identifier of the entry to update.
        :param field_name: The name of the field to delete.
        :return: True if the field was successfully deleted, False otherwise.
        """
        return self.all.delete_field(id, field_name)
    

    def create_track_entry(self, guid, pipeline):
        """
        Create a new track entry in the MongoDB collection.
        :param guid: The unique identifier of the asset.
        :param pipeline: The value for the 'pipeline' field.
        Returns a boolean denoting success or failure.  
        """
        model = track_model.TrackModel(guid, pipeline)
        entry_data = model.get_entry_data()

        if self.get_entry("_id", guid) is None:
            # Insert the new document into the collection
            self.collection.insert_one(entry_data)
            return True
        else:
            return False
        
    def create_test_entry(self, test_entry):
        self.collection.insert_one(test_entry)
    
    def error_get_entry(self):

        """
        Retrieve an entry from the MongoDB collection a field value indicates an error.

        :return: A entry or none if no errors.
        """
        
        error_query = {
            "$or": [
                {"jobs_status": {"$eq": "ERROR"}},
                {"files_status": {"$eq": "ERROR"}},
                {"has_open_share": {"$eq": "ERROR"}},
                {"is_in_ars": {"$eq": "ERROR"}},
                {"erda_sync": {"$eq": "ERROR"}},
                {"has_new_file": {"$eq": "ERROR"}},
                {"hpc_ready": {"$eq": "ERROR"}},
                {"update_metadata": {"$eq": "ERROR"}}
            ]
        }
        
        entry = self.collection.find_one(error_query)
        return entry
    
    def get_error_entries(self):

        """
        Retrieve entries from the MongoDB collection with a flag field value set to error.

        :return: A list of entries, empty if none was found.
        """
        
        error_query = {
            "$or": [
                {"jobs_status": {"$eq": "ERROR"}},
                {"files_status": {"$eq": "ERROR"}},
                {"has_open_share": {"$eq": "ERROR"}},
                {"is_in_ars": {"$eq": "ERROR"}},
                {"erda_sync": {"$eq": "ERROR"}},
                {"has_new_file": {"$eq": "ERROR"}},
                {"hpc_ready": {"$eq": "ERROR"}},
                {"update_metadata": {"$eq": "ERROR"}}
            ]
        }
        
        entries = list(self.collection.find(error_query))
        
        return entries

    def get_paused_entries(self):
        """
        Retrieve entries from the MongoDB collection with a flag field value indicating its paused.

        :return: A list of entries, empty if none was found.
        """
    
        pause_query = {
                "$or": [
                    {"jobs_status": {"$eq": "PAUSED"}},
                    {"files_status": {"$eq": "PAUSED"}},
                    {"has_open_share": {"$eq": "PAUSED"}},
                    {"is_in_ars": {"$eq": "PAUSED"}},
                    {"erda_sync": {"$eq": "PAUSED"}},
                    {"has_new_file": {"$eq": "PAUSED"}},
                    {"hpc_ready": {"$eq": "PAUSED"}},
                    {"update_metadata": {"$eq": "PAUSED"}}
                    ]
                }
    
        entries = list(self.collection.find(pause_query))

        return entries

    def create_derivative_track_entry(self, guid, pipeline, asset_type=AssetTypeEnum.UNKNOWN.value):
        """
        Create a new track entry in the MongoDB collection for a derivative.

        :param guid: The unique identifier of the asset.
        :param pipeline: The value for the 'pipeline' field.
        :return: A boolean denoting success or failure.
        """
        model = track_model.TrackModel(guid, pipeline, asset_type, derivative=True)
        entry_data = model.get_entry_data()
        print(pipeline)
        if self.get_entry("_id", guid) is None:
            # Insert the new document into the collection
            print(guid)
            self.collection.insert_one(entry_data)
            return True
        else:
            return False
    
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
    
    def update_track_job_data_point(self, guid, job_key, job_value, key, value):
        """
            Update an existing track_entrys job with a new value for a key in the MongoDB collection.

            :param guid: The unique identifier of the entry.
            :param job_key: The key identifier for the job to be updated.
            :param job_value: The value identifier for the job to be updated.
            :param key: The key (field) to be updated or created.
            :param value: The new value for the specified key.
            :return: A boolean denoting success or failure.
        """
        # Retrieve the entry
        entry = self.get_entry("_id", guid)
        if entry is None:
            return False

        # Check if the job exists in the job_list
        job_exists = any(d[job_key] == job_value for d in entry.get('job_list', []))
        if not job_exists:
            return False

        self.collection.update_one({"_id": guid, f"job_list.{job_key}": job_value}, {"$set": {f"job_list.$.{key}": value}})

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

    # TODO needs testing
    def update_asset_type(self, guid, type):
        """
        Update the asset type of an entry in the database and, if the new type is 'DEVICE_TARGET',
        remove any jobs with a status of 'WAITING' from the job list.

        :param guid: The unique identifier of the entry to be updated.
        :param type: The new asset type to be set.
        :return: A boolean indicating the success of the operation.
        """
        self.update_entry(guid, "asset_type", type)

        if type == AssetTypeEnum.DEVICE_TARGET.value:
            # Fetch the current entry using the guid to access its job list
            entry = self.get_entry("_id", guid)
        
            # Filter out the jobs with status "WAITING"
            updated_job_list = [job for job in entry["job_list"] if job["status"] != "WAITING"]
        
            # Update the entry with the filtered job list
            self.update_entry(guid, "job_list", updated_job_list)
        
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
    
    def update_track_job_list(self, guid, job, key, value):
        """
            Update an existing entry for a job in the track MongoDB collection.

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

        # Check if the job exists in the file_list
        job_exists = any(d['name'] == job for d in entry.get('job_list', []))
        if not job_exists:
            return False

        query = {"_id": guid, "job_list.name": job}
        job_entry = f"job_list.$.{key}"
        update_data = {"$set": {job_entry: value}}

        self.collection.update_one(query, update_data)

        return True

    # This can probably be made easier by just finding jobs that are running and getting the time stamps for those. Will depend on implementation in app script.
    # TODO missing unit test, not in use - needs way to know which config value to compare to
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
    # TODO missing unit test, not in use - needs way to know which config value to compare to
    def find_queued_jobs_older_than(self):
        """
                Finds an entry based on its job_queued_time compared to current time and the max time set in the config file. 

                :return the first entry with a timestamp too old
        """
        max_time = self.util.get_value(self.slurm_config_path, "max_expected_time_in_queue")
        
        time_ago = datetime.now() - timedelta(hours=max_time)

        result = self.collection.find({"job_list.job_queued_time": {"$lt": time_ago}})
        
        return result


    def get_job_info(self, guid, job_name):
        """
                Finds a job based the asset and the name of the job.
                :returns the job info or none
        """        
        result = self.collection.find_one({ "_id": guid, "job_list.name": job_name },{ "job_list.$": 1 })
        
        # get the actual job info from the resulting dictionary
        if result and "job_list" in result:
            result = result["job_list"][0]
            return result
        
        return None
    
    def get_job_from_key_value(self, guid, key, value):
        """
                Finds a job based on the asset and a key value pair of the job.
                :returns the job info or none
        """

        job_key = f"job_list.{key}"

        result = self.collection.find_one({ "_id": guid, job_key: value },{ "job_list.$": 1 })
        
        # get the actual job info from the resulting dictionary
        if result and "job_list" in result:
            result = result["job_list"][0]
            return result
        
        return None