import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from Connections import connections
from MongoDB import track_repository
from Enums import status_enum, validate_enum
import utility
import time
from HealthUtility import health_caller, run_utility

"""
Responsible for checking availability on slurm. Will have to wait for later to be made. For now assuming there always is capacity. 
"""
# TODO Check that HPC is available. Get some status from mongo db. Other service responsible for updating that. 
class HPCJobCaller():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        # service name for logging/info purposes
        self.service_name = "HPC job caller"

        self.ssh_config_path = f"{project_root}/ConfigFiles/ucloud_connection_config.json"
        self.job_detail_path = f"{project_root}/ConfigFiles/job_detail_config.json"
        self.run_config_path = f"{project_root}/ConfigFiles/run_config.json"
        self.mongo_track = track_repository.TrackRepository()
        self.util = utility.Utility()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum
        self.cons = connections.Connections()

        # set the config file value to RUNNING, mostly for ease of testing
        self.util.update_json(self.run_config_path, self.service_name, self.status_enum.RUNNING.value)

        self.run_util = run_utility.RunUtility(self.service_name, self.run_config_path, self.log_filename, self.logger_name)

        entry = self.run_util.log_msg(f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        self.con = self.create_ssh_connection()
        
        self.run = self.run_util.get_service_run_status()
        self.run_util.service_run = self.run
        
        self.loop()
    
    def create_ssh_connection(self):
        self.cons.create_ssh_connection(self.ssh_config_path)
        # handle when connection wasnt established - calls health service and sets run config to STOPPED
        if self.cons.exc is not None:
            entry = self.run_util.log_exc(self.cons.msg, self.cons.exc, self.status_enum.ERROR.value)
            self.health_caller.warning(self.service_name, entry)
            self.util.update_json(self.run_config_path, self.service_name, self.status_enum.STOPPED.value)
        
        return self.cons.get_connection()

    def loop(self):

        while self.run == status_enum.StatusEnum.RUNNING.value:
            
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

            # checks if service should keep running - configurable in ConfigFiles/run_config.json            
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.validate_enum.PAUSED.value:
                self.run = self.run_util.pause_loop()

        # outside main while loop        
        self.mongo_track.close_connection()
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