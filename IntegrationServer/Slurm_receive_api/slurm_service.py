import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from MongoDB import mongo_connection

class SlurmService():

    def __init__(self):
        self.util = utility.Utility()
        self.mongo_track = mongo_connection.MongoConnection("track")
        self.mongo_metadata = mongo_connection.MongoConnection("metadata")

    # calls other functions to update specific files and mongoDB
    def update_from_slurm(self, guid, job, status, dictionary):
        
        self.update_mongo_track(guid, job, status)

        self.update_jobs_json(guid, job, status)

        if status == "DONE":
            self.update_mongo_metadata(guid, dictionary)

            self.update_metadata_json(guid, dictionary)

    def update_mongo_track(self, guid, job, status):
        
        self.mongo_track.update_track_job_status(guid, job, status)

    def update_jobs_json(self, guid, job, status):
        pass

    def update_mongo_metadata(self, guid, dictionary):
        pass

    def update_metadata_json(self, guid, dictionary):
        pass
