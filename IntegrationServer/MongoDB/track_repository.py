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
    
    def create_derivative_track_entry(self, guid, pipeline):
        """
        Create a new track entry in the MongoDB collection for a derivative.

        :param guid: The unique identifier of the asset.
        :param pipeline: The value for the 'pipeline' field.
        :return: A boolean denoting success or failure.
        """
        model = track_model.TrackModel(guid, pipeline, derivative=True)
        entry_data = model.get_entry_data()

        if self.get_entry("_id", guid) is None:
            # Insert the new document into the collection
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

    