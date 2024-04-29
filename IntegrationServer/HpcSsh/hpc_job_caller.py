import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from Connections import connections
from MongoDB import mongo_connection
from Enums import status_enum, validate_enum
import utility
import time

"""
Responsible for checking availability on slurm. Will have to wait for later to be made. For now assuming there always is capacity. 
"""
# TODO Check that HPC is available. Get some status from mongo db. Other service responsible for updating that. 
class HPCJobCaller:

    def __init__(self):

        self.ssh_config_path = f"{project_root}/ConfigFiles/ucloud_connection_config.json"
        self.job_detail_path = f"{project_root}/ConfigFiles/job_detail_config.json"

        self.run = True
        self.count = 2

        self.cons = connections.Connections()
        self.util = utility.Utility()
        self.mongo_track = mongo_connection.MongoConnection("track")

        self.cons.create_ssh_connection(self.ssh_config_path)
        self.con = self.cons.get_connection()

        self.loop()
    
    def loop(self):
        
        while self.run:
            
            asset = None
            asset = self.mongo_track.get_entry_from_multiple_key_pairs([{"hpc_ready": validate_enum.ValidateEnum.YES.value, 
                                                                         "jobs_status": status_enum.StatusEnum.WAITING.value}])
            
            if asset is None:
                
                time.sleep(1)        
            else:    
                guid, jobs = self.get_guid_and_jobs(asset)
                
                for job in jobs:
                    
                    name = job["name"]

                    job_details = self.util.get_value(self.job_detail_path, name)
                    script_path = job_details["script"]

                    self.mongo_track.update_track_job_status(guid, name, status_enum.StatusEnum.STARTING.value)
                    self.mongo_track.update_entry(guid, "jobs_status", status_enum.StatusEnum.STARTING.value)

                    print(script_path, name)
                    self.con.ssh_command(f"bash {script_path} {guid}")
                    time.sleep(1)

            self.count -= 1

            if self.count == 0:
                self.run = False
                self.cons.close_connection()


    def get_guid_and_jobs(self, asset):

        jobs = []    

        guid = asset["_id"]

        all_jobs = asset["job_list"]
        waiting_jobs = []

        for job in all_jobs:

            if job["status"] == status_enum.StatusEnum.WAITING.value:
                waiting_jobs.append(job)

        # Specify the field for which you want to find the lowest value
        field_to_check = "priority"

        # Find the lowest value
        lowest_value = min(job[field_to_check] for job in waiting_jobs)

        # Collect entries with the lowest value
        jobs = [job for job in waiting_jobs if job[field_to_check] == lowest_value]

        return guid, jobs

if __name__ == '__main__':
    HPCJobCaller()