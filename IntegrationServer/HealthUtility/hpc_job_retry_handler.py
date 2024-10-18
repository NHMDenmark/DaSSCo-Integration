import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from datetime import datetime, timedelta
import utility
from MongoDB import service_repository, track_repository
from HealthUtility import health_caller, run_utility
from Enums import status_enum, validate_enum, flag_enum

"""
Service that handles assets which have jobs that have been updated with the retry status.
"""
class HPCJobRetryHandler():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        
        # service name for logging/info purposes
        self.service_name = "HPC job retry handler"
        self.prefix_id= "Hjrh"

        self.util = utility.Utility()
        self.service_mongo = service_repository.ServiceRepository()
        self.track_mongo = track_repository.TrackRepository()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum
        self.flag_enum = flag_enum.FlagEnum

        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name)
        
        # set the service db value to RUNNING, mostly for ease of testing
        self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.RUNNING.value)
        
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        self.run = self.run_util.get_service_run_status()
        
        try:
            self.loop()
        except Exception as e:
            print("service crashed", e)

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            # find asset with jobs_status = RETRY
            asset = self.track_mongo.get_entry(self.flag_enum.JOBS_STATUS.value, self.status_enum.RETRY.value)

            if asset is None:
                time.sleep(30)
                self.end_of_loop_checks()
                continue
            
            guid = asset["_id"]
            print(f"found {guid}")

            # find the job that has the RETRY status
            job = self.track_mongo.get_job_from_key_value(guid, "status", self.status_enum.RETRY.value)
            
            job_name = job["name"]

            # check if the job is set to retry for the 3rd time. If so set jobs status and job status as ERROR
            first_job_try = self.track_mongo.get_job_info(guid, f"attempt_1_{job_name}")
            second_job_try = None

            if first_job_try is not None:
                second_job_try = self.track_mongo.get_job_info(guid, f"attempt_2_{job_name}")
            
            if second_job_try is not None:
                self.track_mongo.update_track_job_status(guid, job_name, self.status_enum.ERROR.value)
                self.track_mongo.update_entry(guid, self.flag_enum.JOBS_STATUS.value, self.status_enum.ERROR.value)

                entry = self.run_util.log_msg(self.prefix_id, f"{guid} received RETRY status twice before for {job_name}. Job status is being set to ERROR.", self.status_enum.ERROR.value)
                self.health_caller.error(self.service_name, entry, guid)
                
                self.end_of_loop_checks()
                continue            

            # change old job status to FAILED, change old job name to attempt_1_jobname or attempt_2_jobname
            self.track_mongo.update_track_job_status(guid, job_name, self.status_enum.FAILED.value)
            if first_job_try is None:
                self.track_mongo.update_track_job_list(guid, job_name, "name", f"attempt_1_{job_name}")
            else:
                self.track_mongo.update_track_job_list(guid, job_name, "name", f"attempt_2_{job_name}")

            # add/create a copy of that job and set the jobs_status to WAITING
            job["status"] = self.status_enum.WAITING.value
            job["hpc_job_id"] = -9
            job["job_queued_time"] = None
            job["job_start_time"] = None

            self.track_mongo.append_existing_list(guid, "job_list", job)

            self.track_mongo.update_entry(guid, "jobs_status", self.status_enum.WAITING.value)

            # set additional flags depending on which job we are dealing with
            if job["name"] == "assetLoader":
                self.track_mongo.update_entry(guid, "hpc_ready", self.validate_enum.NO.value)

            if job["name"] == "clean_up":
                self.track_mongo.update_entry(guid, "hpc_ready", self.validate_enum.YES.value)

            if job["name"] == "uploader":
                self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.YES.value)

            # Notification of event
            entry = self.run_util.log_msg(self.prefix_id, f"{guid} will reattempt {job_name} after HPC sent RETRY status back.")
            self.health_caller.warning(self.service_name, entry, guid)

            self.end_of_loop_checks()
        
        # outside loop
        self.close_all_connections()

    # end of loop checks
    def end_of_loop_checks(self):
        # checks if service should keep running           
        self.run = self.run_util.check_run_changes()

        # Pause loop
        if self.run == self.validate_enum.PAUSED.value:
            self.run = self.run_util.pause_loop()
    
    def close_all_connections(self):
        try:
            self.track_mongo.close_connection()
            self.service_mongo.close_connection()
            self.run_util.service_mongo.close_connection()
        except:
            pass

if __name__ == "__main__":
    HPCJobRetryHandler()