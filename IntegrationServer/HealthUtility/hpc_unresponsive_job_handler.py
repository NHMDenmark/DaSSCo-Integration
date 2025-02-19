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
Service that handles assets which have jobs that never gave an answer after being run. Their jobs_status would then be stuck with the "STARTING" or "RUNNING" status.
"""
class HPCUnresponsiveJobHandler():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        
        # service name for logging/info purposes
        self.service_name = "HPC unresponsive job handler"
        self.prefix_id= "Hujh"

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
            try:
                entry = self.run_util.log_exc(self.prefix_id, f"{self.service_name} crashed.", e)
                self.health_caller.unexpected_error(self.service_name, entry)
            except:
                print(f"failed to inform about crash")
            self.close_all_connections()

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            unresponsive_starting_list = []
            unresponsive_running_list = []
            starting_tuple_list = []
            running_tuple_list = []

            starting_asset_list = self.track_mongo.get_entries_from_multiple_key_pairs([{self.flag_enum.JOBS_STATUS.value: self.status_enum.STARTING.value}])
            
            for asset in starting_asset_list:
                guid = asset["_id"]
                asset_job = self.track_mongo.get_job_from_key_value(guid, "status", self.status_enum.STARTING.value)
                
                # jobs_status starting can have both starting and queued status for the specific job
                if asset_job is None: 
                    asset_job = self.track_mongo.get_job_from_key_value(guid, "status", self.status_enum.QUEUED.value)

                if asset_job is not None:
                    job_name = asset_job["name"]
                else:
                    # TODO handle this scenario so asset doesnt loop around here forever
                    continue
                
                asset_tuple = (asset, guid, job_name)

                starting_tuple_list.append(asset_tuple)
                
            running_asset_list = self.track_mongo.get_entries_from_multiple_key_pairs([{self.flag_enum.JOBS_STATUS.value: self.status_enum.RUNNING.value}])
            
            for asset in running_asset_list:
                guid = asset["_id"]
                asset_job = self.track_mongo.get_job_from_key_value(guid, "status", self.status_enum.RUNNING.value)

                if asset_job is not None:
                    job_name = asset_job["name"]
                    hpc_job_id = asset_job["hpc_job_id"]
                else:
                    # TODO handle this scenario so asset doesnt loop around here forever
                    continue
                
                asset_tuple = (asset, guid, job_name, hpc_job_id)

                running_tuple_list.append(asset_tuple)

            # TODO decide if queued here
            #queued_asset_list = self.track_mongo.get_entries_from_multiple_key_pairs()
            
            wait_time = 600
            time.sleep(wait_time)

            for asset_tuple in starting_tuple_list:
                asset, guid, job_name = asset_tuple

                current_asset_job = self.track_mongo.get_job_from_key_value(guid, "status", self.status_enum.STARTING.value)

                if current_asset_job is None:
                    current_asset_job = self.track_mongo.get_job_from_key_value(guid, "status", self.status_enum.QUEUED.value)

                current_job_name = current_asset_job["name"]
                if asset[self.flag_enum.JOBS_STATUS.value] == self.status_enum.STARTING.value and job_name == current_job_name:
                    unresponsive_starting_list.append(asset_tuple)

            for asset_tuple in running_tuple_list:
                asset, guid, job_name, hpc_job_id = asset_tuple

                current_asset_job = self.track_mongo.get_job_from_key_value(guid, "status", self.status_enum.RUNNING.value)
                current_job_name = current_asset_job["name"]
                if asset[self.flag_enum.JOBS_STATUS.value] == self.status_enum.RUNNING.value and job_name == current_job_name:
                    unresponsive_running_list.append(asset_tuple)

            if len(unresponsive_running_list) == 0 and len(unresponsive_starting_list) == 0:
                self.end_of_loop_checks()
                continue
            else:
                print(f"Found {len(unresponsive_starting_list)} unresponsive jobs with starting status")
                for asset_tuple in unresponsive_starting_list:
                    
                    asset, guid, job_name = asset_tuple

                    self.track_mongo.update_track_job_status(guid, job_name, self.status_enum.RETRY.value)

                    entry = self.run_util.log_msg(self.prefix_id, f"{guid} had {job_name} not responding for more than {wait_time} seconds while status was {self.status_enum.STARTING.value}. Setting status for {self.flag_enum.JOBS_STATUS.value} to {self.status_enum.RETRY.value}. Hpc job retry handler will take over.")
                    sent = self.health_caller.warning(self.service_name, entry, guid, self.flag_enum.JOBS_STATUS.value, self.status_enum.RETRY.value)
                    # TODO handle "sent"
                    

                print(f"Found {len(unresponsive_running_list)} unresponsive jobs with running status")
                for asset_tuple in unresponsive_running_list:
                    
                    asset, guid, job_name, hpc_job_id = asset_tuple

                    self.track_mongo.update_track_job_status(guid, job_name, self.status_enum.RETRY.value)

                    entry = self.run_util.log_msg(self.prefix_id, f"{guid} had {job_name}, hpc job id : {hpc_job_id}, not respond for more than {wait_time} seconds while status was {self.status_enum.RUNNING.value}. Setting status for {self.flag_enum.JOBS_STATUS.value} to {self.status_enum.RETRY.value}. Hpc job retry handler will take over.")
                    sent = self.health_caller.warning(self.service_name, entry, guid, self.flag_enum.JOBS_STATUS.value, self.status_enum.RETRY.value)
                    # TODO handle "sent"

            self.end_of_loop_checks()
    
        # outside loop
        self.close_all_connections()
        print(f"{self.service_name} shutdown")

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
    HPCUnresponsiveJobHandler()