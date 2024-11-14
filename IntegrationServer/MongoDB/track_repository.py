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

    def __init__(self):
        self.util = utility.Utility()
        self.mongo_track = mongo_connection.MongoConnection("track")

        self.collection = self.mongo_track.get_collection()
        self.all = all_repository.AllRepository(self.collection)

    def close_connection(self):
        self.mongo_track.close_mdb()

    """
    Returns true if there is no issue, else returns the exception.
    """
    def check_connection(self):
        try:
            reply = self.mongo_track.ping_connection()
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

    def create_track_entry(self, guid, pipeline):
        """
        Create a new track entry in the MongoDB collection.

        :param guid: The unique identifier of the asset.
        :param pipeline: The value for the 'pipeline' field.
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
            entry = self.get_entry(guid)
        
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