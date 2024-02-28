import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from MongoDB import mongo_connection
from Enums.status_enum import StatusEnum
from Enums import validate_enum

class SlurmService():

    def __init__(self):
        self.util = utility.Utility()
        self.status = StatusEnum
        self.mongo_track = mongo_connection.MongoConnection("track")
        self.mongo_metadata = mongo_connection.MongoConnection("metadata")

    def persist_new_metadata(self, new_metadata):
        metadata_json = new_metadata.__dict__
        self.util.write_full_json(f"{project_root}/Files/NewFiles/Derivatives/{new_metadata.asset_guid}.json", metadata_json)

    # calls other functions to update specific files and mongoDB
    # TODO send success message back to slurm?
    def update_from_slurm(self, update_data):
        # Extract data from the input
        guid = update_data.guid
        job = update_data.job
        update_status = update_data.status
        data_dict = dict(update_data.data)

        # Update MongoDB track
        self.update_mongo_track(guid, job, update_status)

        # Update jobs JSON file
        self.update_jobs_json(guid, job, update_status)

        # If status is 'DONE', update MongoDB metadata and metadata JSON file
        if update_status == self.status.DONE.value:
            
            self.update_mongo_metadata(guid, data_dict)

            self.update_metadata_json(guid, data_dict)
        
        if update_status == self.status.ERROR.value:
            # TODO handle error
            pass

    def update_mongo_track(self, guid, job, status):
        # Update MongoDB track with job status
        self.mongo_track.update_track_job_status(guid, job, status)

    def update_jobs_json(self, guid, job, status):
        # Extract pipeline name and batch date from MongoDB metadata
        pipeline = self.mongo_metadata.get_value_for_key(guid, "pipeline_name")
        batch_date = self.mongo_metadata.get_value_for_key(guid, "date_asset_taken")[:10]

        # Define job file name and path
        job_file_name = guid + "_jobs.json"
        in_process_path = os.path.join(project_root, "Files\InProcess")        
        job_file_path = os.path.join(in_process_path, f"{pipeline}\{batch_date}\{guid}\{job_file_name}")

        # Update jobs JSON file
        self.util.update_json(job_file_path, job, status)

    def update_mongo_metadata(self, guid, dictionary):
        # Update MongoDB metadata with key-value pairs from the dictionary
        for key, value in dictionary.items():
            self.mongo_metadata.update_entry(guid, key, value)

    def update_metadata_json(self, guid, dictionary):
        # Extract pipeline name and batch date from MongoDB metadata
        pipeline = self.mongo_metadata.get_value_for_key(guid, "pipeline_name")
        batch_date = self.mongo_metadata.get_value_for_key(guid, "date_asset_taken")[:10]

        # Define metadata file name and path
        metadata_file_name = guid + ".json"
        in_process_path = os.path.join(project_root, "Files\InProcess")
        metadata_file_path = os.path.join(in_process_path, f"{pipeline}\{batch_date}\{guid}\{metadata_file_name}")

        # Update metadata JSON file with key-value pairs from the dictionary
        for key, value in dictionary.items():
            self.util.update_json(metadata_file_path, key, value)

    def job_queued(self, queue_data):

        guid = queue_data.guid
        job_id = queue_data.job_id
        job_name = queue_data.job_name
        job_start_time = queue_data.timestamp

        self.mongo_track.update_track_job_status(guid, job_name, self.status.RUNNING.value)
        self.mongo_track.update_track_job_new(guid, job_name, "slurm_job_id", job_id)
        self.mongo_track.update_track_job_new(guid, job_name, "job_start_time", job_start_time)

    def get_httplink(self, asset_guid):
        
        httplink = self.mongo_track.get_value_for_key(asset_guid, "image_httplink")        
        
        return httplink
    
    def get_metadata_asset(self, asset_guid):

        metadata = self.mongo_metadata.get_entry("_id", asset_guid)

        return metadata

    def asset_ready(self, asset_guid):
        self.mongo_track.update_entry(asset_guid, "is_on_hpc", validate_enum.ValidateEnum.YES.value)
