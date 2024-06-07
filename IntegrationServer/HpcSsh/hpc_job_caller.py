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
from HealthUtility import health_caller
from InformationModule.log_class import LogClass

"""
Responsible for checking availability on slurm. Will have to wait for later to be made. For now assuming there always is capacity. 
"""
# TODO Check that HPC is available. Get some status from mongo db. Other service responsible for updating that. 
class HPCJobCaller(LogClass):

    def __init__(self):

<<<<<<< HEAD
        self.ssh_config_path = "/work/data/DaSSCo-Integration/IntegrationServer/ConfigFiles/ucloud_connection_config.json"
        self.job_detail_path = "/work/data/DaSSCo-Integration/IntegrationServer/ConfigFiles/job_detail_config.json"

        self.run = True
        self.count = 2

=======
        # setting up logging
        super().__init__(filename = f"{os.path.basename(os.path.abspath(__file__))}.log", name = os.path.relpath(os.path.abspath(__file__), start=project_root))
        # service name for logging/info purposes
        self.service_name = "HPC job caller"

        self.ssh_config_path = f"{project_root}/ConfigFiles/ucloud_connection_config.json"
        self.job_detail_path = f"{project_root}/ConfigFiles/job_detail_config.json"
        self.run_config_path = f"{project_root}/ConfigFiles/run_config.json"
        self.mongo_track = track_repository.TrackRepository()
>>>>>>> origin
        self.util = utility.Utility()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.cons = connections.Connections()

<<<<<<< HEAD
        #self.cons = connections.Connections()
        #self.cons.create_ssh_connection(self.ssh_config_path)
        #self.con = self.cons.get_connection()
=======
        # set the config file value to RUNNING, mostly for ease of testing
        self.util.update_json(self.run_config_path, self.service_name, self.status_enum.RUNNING.value)
>>>>>>> origin

        self.con = self.create_ssh_connection()

        self.run = self.util.get_value(self.run_config_path, self.service_name)        
        self.loop()
    
    def create_ssh_connection(self):
        self.cons.create_ssh_connection(self.ssh_config_path)
        # handle when connection wasnt established - calls health service and sets run config to STOPPED
        if self.cons.exc is not None:
            entry = self.log_exc(self.cons.msg, self.cons.exc, self.status_enum.ERROR.value)
            self.health_caller.warning(self.service_name, entry)
            self.util.update_json(self.run_config_path, self.service_name, self.status_enum.STOPPED.value)
        
        return self.cons.get_connection()

    def loop(self):

        while self.run == status_enum.StatusEnum.RUNNING.value:
            
            asset = self.mongo_track.get_entry_from_multiple_key_pairs([{"hpc_ready": validate_enum.ValidateEnum.YES.value, 
                                                                         "jobs_status": status_enum.StatusEnum.WAITING.value}])
            
            if asset is None:
<<<<<<< HEAD
                
                time.sleep(10)        
=======
                time.sleep(1)        
>>>>>>> origin
            else:    
                guid, jobs = self.get_guid_and_jobs(asset)
                
                cons = connections.Connections()
                cons.create_ssh_connection(self.ssh_config_path)
                con = cons.get_connection()

                for job in jobs:
                    
                    name = job["name"]

                    job_details = self.util.get_value(self.job_detail_path, name)
                    script_path = job_details["script"]

                    self.mongo_track.update_track_job_status(guid, name, status_enum.StatusEnum.STARTING.value)
                    self.mongo_track.update_entry(guid, "jobs_status", status_enum.StatusEnum.STARTING.value)

                    print(script_path, name)
<<<<<<< HEAD
                    con.ssh_command(f"bash {script_path} {guid}")
                    
                time.sleep(3)
                cons.close_connection()

            # self.count -= 1
            run_config_path = f"{project_root}/ConfigFiles/run_config.json"
            
            run = self.util.get_value(run_config_path, "run")
            if run == "False":
                self.run = False
                #self.cons.close_connection()
            if self.count == 0:
                self.run = False
                #self.cons.close_connection()
=======
                    self.con.ssh_command(f"bash {script_path} {guid}")
                    time.sleep(1)

            # checks if service should keep running - configurable in ConfigFiles/run_config.json
            all_run = self.util.get_value(self.run_config_path, "all_run")
            service_run = self.util.get_value(self.run_config_path, self.service_name)

            # Pause loop
            counter = 0
            while service_run == self.status_enum.PAUSED.value:
                sleep = 10
                counter += 1
                time.sleep(sleep)
                wait_time = sleep * counter
                entry = self.log_msg(f"{self.service_name} has been in pause mode for ~{wait_time} seconds")
                self.health_caller.warning(self.service_name, entry)
                service_run = self.util.get_value(self.run_config_path, self.service_name)
                
                all_run = self.util.get_value(self.run_config_path, "all_run")
                if all_run == self.status_enum.STOPPED.value:
                    service_run = self.status_enum.STOPPED.value
                
                if service_run != self.status_enum.PAUSED.value:
                    entry = self.log_msg(f"{self.service_name} has changed run status from {self.status_enum.PAUSED.value} to {service_run}")                   
                    self.health_caller.warning(self.service_name, entry)

            if all_run == self.status_enum.STOPPED.value or service_run == self.status_enum.STOPPED.value:
                self.run = self.status_enum.STOPPED.value

        # outside main while loop        
        self.mongo_track.close_connection()
        self.cons.close_connection()
>>>>>>> origin


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
