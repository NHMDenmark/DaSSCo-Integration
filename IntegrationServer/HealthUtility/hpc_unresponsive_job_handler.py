import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from datetime import datetime, timedelta
import utility
from MongoDB.mongo_connection import MongoSharedClient
from MongoDB import track_repository, service_repository, metadata_repository
from Connections import connections
from StorageApi import storage_client
from HealthUtility import health_caller, run_utility
from Enums import status_enum, validate_enum, flag_enum, asset_status_nt
from socket import timeout
from dotenv import load_dotenv

"""
Service that handles assets which have jobs that never gave an answer after being run. Their jobs_status would then be stuck with the "STARTING" or "RUNNING" status.
"""
class HPCUnresponsiveJobHandler():

    def __init__(self):

        load_dotenv()

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        self.pid = os.getpid()
        # service name for logging/info purposes
        self.service_name = "HPC unresponsive job handler"
        self.prefix_id= "Hujh"
        self.ssh_config_name = os.getenv("SLURM_CONFIGURATION")
        self.hpc_asset_directory = os.getenv("HPC_ASSET_DIRECTORY")

        self.util = utility.Utility()
        self.mongo_client = MongoSharedClient()
        self.track_mongo = track_repository.TrackRepository(self.mongo_client)
        self.service_mongo = service_repository.ServiceRepository(self.mongo_client)
        self.metadata_mongo = metadata_repository.MetadataRepository(self.mongo_client)
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum
        self.flag_enum = flag_enum.FlagEnum
        self.asset_status_nt = asset_status_nt.AssetStatusNT
        self.cons = connections.Connections(self.mongo_client)

        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name, self.pid, self.mongo_client)
        
        self.run_util.service_starting_updates()        
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        self.con = self.create_ssh_connection()

        self.run = self.run_util.get_service_run_status()
        
        try:
            self.loop()
        except Exception as e:
            print("service crashed", e)
            try:
                entry = self.run_util.log_exc(self.prefix_id, f"{self.service_name} crashed.", e, self.status_enum.CRITICAL_ERROR.value)
                self.health_caller.unexpected_error(self.service_name, entry)
            except:
                print(f"failed to inform about crash")
            self.run_util.service_stopping_updates()
            self.close_db_connections()


    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            unresponsive_starting_list = []
            unresponsive_running_list = []
            starting_tuple_list = []
            running_tuple_list = []

            starting_asset_list = self.track_mongo.get_entries_from_multiple_key_pairs([{self.flag_enum.JOBS_STATUS.value: self.status_enum.STARTING.value}, {self.flag_enum.AVAILABLE_FOR_SERVICES.value: self.validate_enum.YES.value}])
            
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
                
            running_asset_list = self.track_mongo.get_entries_from_multiple_key_pairs([{self.flag_enum.JOBS_STATUS.value: self.status_enum.RUNNING.value}, {self.flag_enum.AVAILABLE_FOR_SERVICES.value: self.validate_enum.YES.value}])
            
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
            
            wait_time = 1800
            time.sleep(wait_time)

            for asset_tuple in starting_tuple_list:
                asset, guid, job_name = asset_tuple

                current_asset_job = self.track_mongo.get_job_from_key_value(guid, "status", self.status_enum.STARTING.value)

                if current_asset_job is None:
                    current_asset_job = self.track_mongo.get_job_from_key_value(guid, "status", self.status_enum.QUEUED.value)
                
                if current_asset_job is not None:
                    current_job_name = current_asset_job["name"]
                else:
                    continue
                
                if asset[self.flag_enum.JOBS_STATUS.value] == self.status_enum.STARTING.value and job_name == current_job_name:
                    unresponsive_starting_list.append(asset_tuple)

            for asset_tuple in running_tuple_list:
                asset, guid, job_name, hpc_job_id = asset_tuple

                current_asset_job = self.track_mongo.get_job_from_key_value(guid, "status", self.status_enum.RUNNING.value)
                
                if current_asset_job is not None:
                    current_job_name = current_asset_job["name"]
                else:
                    continue

                if asset[self.flag_enum.JOBS_STATUS.value] == self.status_enum.RUNNING.value and job_name == current_job_name:
                    unresponsive_running_list.append(asset_tuple)

            if len(unresponsive_running_list) == 0 and len(unresponsive_starting_list) == 0:
                self.end_of_loop_checks()
                continue
            else:
                print(f"Found {len(unresponsive_starting_list)} unresponsive jobs with starting status")
                for asset_tuple in unresponsive_starting_list:
                    
                    asset, guid, job_name = asset_tuple
                    should_retry = False

                    # TODO contact slurm and check status there, remove from slurm queue or handle accordingly if job is still running there, if not then set to retry
                    slurm_job_status = self.get_slurm_job_status(self, hpc_job_id)

                    if slurm_job_status is not False:
                        state = []
                        for job in slurm_job_status:
                            state.append(job["state"])

                        if "CONPLETED" in state:
                            should_retry = self.handle_completed_state(guid, job_name, hpc_job_id)

                        elif "RUNNING" in state or "PENDING" in state:
                            should_retry = self.handle_running_or_pending_state()

                        elif "FAILED" in state or "CANCELLED" in state or "TIMEOUT" in state or "OUT_OF_MEMORY" in state or "NODE_FAIL" in state or "PREEMPTED" in state:
                            should_retry = self.handle_failed_state()

                        else:
                            #TODO handle as total failure
                            should_retry = self.handle_unknown_state()

                    elif slurm_job_status is False:
                        self.end_of_loop_checks()

                    if should_retry is True:
                        self.track_mongo.update_track_job_status(guid, job_name, self.status_enum.RETRY.value)
                        entry = self.run_util.log_msg(self.prefix_id, f"{guid} had {job_name} not responding for more than {wait_time} seconds while status was {self.status_enum.STARTING.value}. Setting status for {self.flag_enum.JOBS_STATUS.value} to {self.status_enum.RETRY.value}. Hpc job retry handler will take over.")
                        sent = self.health_caller.warning(self.service_name, entry, guid, self.flag_enum.JOBS_STATUS.value, self.status_enum.RETRY.value)
                        # TODO handle "sent"

                    elif should_retry is False:
                        #TODO handle
                        pass                    

                print(f"Found {len(unresponsive_running_list)} unresponsive jobs with running status")
                for asset_tuple in unresponsive_running_list:
                    
                    asset, guid, job_name, hpc_job_id = asset_tuple

                    # TODO contact slurm and check status there, remove from slurm queue or handle accordingly if job is still running there, if not then set to retry
                    slurm_job_status = self.get_slurm_job_status(self, hpc_job_id)
                    
                    if slurm_job_status is False:
                        self.end_of_loop_checks()

                    print(f"Handling {guid} with job {job_name} and hpc job id {hpc_job_id}")

                    self.track_mongo.update_track_job_status(guid, job_name, self.status_enum.RETRY.value)

                    entry = self.run_util.log_msg(self.prefix_id, f"{guid} had {job_name}, hpc job id : {hpc_job_id}, not respond for more than {wait_time} seconds while status was {self.status_enum.RUNNING.value}. Setting status for {self.flag_enum.JOBS_STATUS.value} to {self.status_enum.RETRY.value}. Hpc job retry handler will take over.")
                    sent = self.health_caller.warning(self.service_name, entry, guid, self.flag_enum.JOBS_STATUS.value, self.status_enum.RETRY.value)
                    # TODO handle "sent"

            self.end_of_loop_checks()
    
        # outside loop
        self.run_util.service_stopping_updates()
        self.cons.close_connection()
        self.close_db_connections()
        print(f"{self.service_name} shutdown")

    # end of loop checks
    def end_of_loop_checks(self):
        # checks if service should keep running           
        self.run = self.run_util.check_run_changes()

        # Pause loop
        if self.run == self.validate_enum.PAUSED.value:
            self.run = self.run_util.pause_loop()
    
    def close_db_connections(self):
        try:
            self.track_mongo.close_connection()
            self.run_util.service_mongo.close_connection()
        except Exception as e:
            print(f"Failed to close db connections: {e}")

    def create_ssh_connection(self):
            
            self.cons.create_ssh_connection(self.ssh_config_name)
            # handle when connection wasnt established - calls health service and sets run config to STOPPED
            if self.cons.exc is not None:
                entry = self.run_util.log_exc(self.prefix_id, self.cons.msg, self.cons.exc, self.status_enum.ERROR.value)
                self.health_caller.warning(self.service_name, entry)
                self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.STOPPED.value)
            
            return self.cons.get_connection()

    def get_slurm_job_status(self, job_id, connection_fail=0):
        reply = []
        try:
            response = self.con.ssh_command(f"sacct -j {job_id} --noheader --format=JobName,State")
            lines = response.strip().splitlines()
            for line in lines:
                job_name, state = line.split()
                # Remove the trailing '+' if present
                state = state.rstrip("+")  
                job_name = job_name.rstrip("+")
                reply.append({"job_id": job_id, "job_name": job_name, "state": state})
            print(reply)
            
        except Exception as e:
            print(e)
            time.sleep(20)
        
            if isinstance(e, timeout):
                entry = self.run_util.log_msg(self.prefix_id, f"Attempting to reconnect to HPC server after timeout: {e}")
                self.health_caller.warning(self.service_name, entry)
                                        
            else:
                entry = self.run_util.log_msg(self.prefix_id, f"Attempting to reconnect to HPC server after fail: {e}", self.status_enum.ERROR.value)
                self.health_caller.error(self.service_name, entry)
        
            self.con.close()
            self.cons.close_connection()

            if connection_fail == 3:
                entry = self.run_util.log_msg(self.prefix_id, f"Failed to reconnect to HPC server after 3 attempts. Will try pausing service.")
                self.health_caller.warning(self.service_name, entry)

                service_status = self.service_mongo.get_value_for_key(self.service_name, "run_status")
                if service_status != self.status_enum.STOPPED.value:
                    self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.PAUSED.value)
                return False
            else:
                connection_fail += 1
                self.cons = connections.Connections(self.mongo_client)
                self.con = self.create_ssh_connection()
                return self.get_slurm_job_status(job_id, connection_fail)
            
        return reply

    def get_hpc_file_status(self, guid, connection_fail=0):
            
            result = False
            failure_state = False            

            try:
                parent_guids = self.metadata_mongo.get_value_for_key(guid, "parent_guids")
                if parent_guids is not None:
                    parent_guid = parent_guids[0]
                    batchlist_name = self.track_mongo.get_value_for_key(parent_guid, "batch_list_name")              
                else:
                    batchlist_name = self.track_mongo.get_value_for_key(guid, "batch_list_name")

                if batchlist_name is None:
                    # TODO handle not finding a batchlist name
                    print(f"Unable to find batch list name for {guid}") 
                    return False, True
                
                path = os.path.join(self.hpc_asset_directory, batchlist_name)
                
                response = self.con.ssh_command(f"ls -ll {path} | grep {guid}")
                
                lines = response.strip().splitlines()

                if len(lines) < 2:
                    # TODO handle this - note this can be a success for clean up jobs
                    print(f"Did not find 2 files for {guid} in HPC directory {path}")
                    return False, False 
                else:
                    jpeg_line = next((line for line in lines if f"{guid}.jpeg" in line), None)
                    tif_line = next((line for line in lines if f"{guid}.tif" in line), None)
                    json_line = next((line for line in lines if f"{guid}.json" in line), None)

                    if tif_line and json_line:
                        file_size_bytes = int(tif_line.split()[4])
                        file_size_mb = round(file_size_bytes / (1000 * 1000), 0)

                        file_info = self.track_mongo.get_file_info(guid, "tif")

                    elif jpeg_line and json_line:
                        file_size_bytes = int(jpeg_line.split()[4])
                        file_size_mb = round(file_size_bytes / (1000 * 1000), 0)
                        file_info = self.track_mongo.get_file_info(guid, "jpeg")

                    else:
                        # TODO handle this
                        print(f"Did not find matching files pair for {guid} in HPC directory {path}")
                        return False, True

                    expected_file_size = file_info["file_size"]
                    if expected_file_size == file_size_mb:
                        result = True
                    else:
                        print(f"Failed to match file size of {guid} found in track with actual file on HPC.")
                
            except Exception as e:
                print(e)
                time.sleep(20)
            
                if isinstance(e, timeout):
                    entry = self.run_util.log_msg(self.prefix_id, f"Attempting to reconnect to HPC server after timeout: {e}")
                    self.health_caller.warning(self.service_name, entry)
                                            
                else:
                    entry = self.run_util.log_msg(self.prefix_id, f"Attempting to reconnect to HPC server after fail: {e}", self.status_enum.ERROR.value)
                    self.health_caller.error(self.service_name, entry)
            
                self.con.close()
                self.cons.close_connection()
    
                if connection_fail == 3:
                    entry = self.run_util.log_msg(self.prefix_id, f"Failed to reconnect to HPC server after 3 attempts. Will try pausing service.")
                    self.health_caller.warning(self.service_name, entry)
    
                    service_status = self.service_mongo.get_value_for_key(self.service_name, "run_status")
                    if service_status != self.status_enum.STOPPED.value:
                        self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.PAUSED.value)
                    return result, True
                else:
                    connection_fail += 1
                    self.cons = connections.Connections(self.mongo_client)
                    self.con = self.create_ssh_connection()
                    return self.get_hpc_file_status(guid, connection_fail)
                
            return result, failure_state

    def handle_completed_state(self, guid, job_name, hpc_job_id):

        should_continue = self.check_for_job_status_updates(guid, job_name)
        if should_continue is False:
            return False

        # no updates -> check based on job what should happen

        if job_name == "assetLoader":

            storage_api = self.create_storage_api()

            try:
                found, status_code, ars_status, share_size, note = storage_api.get_asset_sharesize_and_status(guid)

                if found is False:
                    entry = self.run_util.log_msg(self.prefix_id, f"Failed getting status from ARS for asset {guid} while trying to handle unresponsive job {job_name} with job id {hpc_job_id}. Job had COMPLETED state in SLURM queue on hpc server, but missing updates to job. Will set jobs_status and job status to {self.status_enum.ERROR.value}.")
                    self.track_mongo.update_track_job_status(guid, hpc_job_id, self.status_enum.ERROR.value)
                    self.run_util.update_metadata_status(guid, self.asset_status_nt.PROCESSING_ISSUE.value)
                    self.health_caller.error(self.service_name, entry, guid, self.flag_enum.JOBS_STATUS.value, self.status_enum.ERROR.value)
                    return False

                if share_size is None:
                    entry = self.run_util.log_msg(self.prefix_id, f"Asset {guid} did not have the expected open file share. This was found while trying to handle unresponsive job {job_name} with job id {hpc_job_id}. Job had COMPLETED state in SLURM queue on hpc server, but missing updates to job. Will set jobs_status and job status to {self.status_enum.CRITICAL_ERROR.value}.")
                    self.track_mongo.update_track_job_status(guid, hpc_job_id, self.status_enum.CRITICAL_ERROR.value)
                    self.run_util.update_metadata_status(guid, self.asset_status_nt.PROCESSING_ISSUE.value)
                    self.health_caller.error(self.service_name, entry, guid, self.flag_enum.JOBS_STATUS.value, self.status_enum.CRITICAL_ERROR.value)
                    return False

            except Exception as e:
                entry = self.run_util.log_exc(self.prefix_id, f"Failed call to ARS during unresponsive hpc job handling for asset {guid}, job {job_name} with id {hpc_job_id}.", e)
                self.health_caller.error(self.service_name, entry)
                return False

            return True

        elif job_name == "clean_up":

            hpc_file_status, failure_state = self.get_hpc_file_status(guid)

            if failure_state is True:
                return False
            
            if hpc_file_status is False:
                # job success
                self.track_mongo.update_track_job_status(guid, job_name, self.status_enum.DONE.value)
                self.track_mongo.update_entry(guid, "jobs_status", self.status_enum.DONE.value)
                self.track_mongo.update_entry(guid, "hpc_ready", self.validate_enum.NO.value)
                self.track_mongo.update_entry(guid, "specify_sync", self.validate_enum.PREPARE.value)
                
                return False
            
            return True

        elif job_name == "uploader":

            storage_api = self.create_storage_api()

            try:
                uploaded = storage_api.check_file_uploaded(guid)

                if uploaded is True:

                    found, files_info, status_code = storage_api.get_files_info(guid)

                    if found:
                        file_format = self.metadata_mongo.get_value_for_key(guid, "file_format")
                        track_file_info = self.track_mongo.get_file_info(guid, file_format)
                        
                        if track_file_info is None:
                            # TODO handle as error
                            print(f"Unable to find file info in track for {guid}")
                            return False
                        
                        expected_check_sum = track_file_info["check_sum"]
                        for file in files_info:
                            if file["crc"] ==  expected_check_sum:
                                # job success
                                self.track_mongo.update_track_job_status(guid, job_name, self.status_enum.DONE.value)
                                self.track_mongo.update_entry(guid, "jobs_status", self.status_enum.DONE.value)
                                self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.AWAIT.value)

                                return False

            except Exception as e:
                entry = self.run_util.log_exc(self.prefix_id, f"Failed call to ARS during unresponsive hpc job handling for asset {guid}, job {job_name} with id {hpc_job_id}.", e)
                self.health_caller.error(self.service_name, entry)
                return False

            return True

        elif job_name == "barcode":
            return True

        elif job_name == "cropping":
            return True

        elif job_name == "derivative":
            pass

        else:
            entry = self.run_util.log_msg(self.prefix_id, f"Asset {guid} had unrecognised {job_name} as job name. Unable to handle this. Will set jobs_status and job status to {self.status_enum.CRITICAL_ERROR.value}.")
            self.track_mongo.update_track_job_status(guid, hpc_job_id, self.status_enum.CRITICAL_ERROR.value)
            self.run_util.update_metadata_status(guid, self.asset_status_nt.PROCESSING_ISSUE.value)
            self.health_caller.error(self.service_name, entry, guid, self.flag_enum.JOBS_STATUS.value, self.status_enum.CRITICAL_ERROR.value)
            return False
        

    def handle_running_or_pending_state(self, hpc_job_id):
        # delete job from slurm queue and set to retry 
        return True

    def handle_failed_state(self):
        # check asset is as it should be in LUMI/ARS then set to retry
        return True

    def handle_unknown_state(self):
        # check asset is as it should be in LUMI/ARS then set to retry or total failure based on what is found
        return False

    def check_for_job_status_updates(self, guid, job_name):
        job_info = self.track_mongo.get_job_info(guid, job_name)
        jobs_status = self.track_mongo.get_value_for_key(guid, self.flag_enum.JOBS_STATUS.value)
        current_job_status = job_info["status"]
                
        if current_job_status == self.status_enum.DONE.value and jobs_status == self.status_enum.DONE.value:
            return False
        else:
            return True

    def create_storage_api(self):
    
        storage_api = storage_client.StorageClient(self.mongo_client)

        if storage_api.client is None:

            # retry
            time.sleep(60)
            storage_api = storage_client.StorageClient(self.mongo_client)

            if storage_api.client is None:
                # TODO decide if exiting is correct here when failing again instead of pausing service.
                # log the failure to create the storage api
                entry = self.run_util.log_exc(self.prefix_id, f"Failed to create storage client twice. {self.service_name} will shut down. Received status: {storage_api.status_code}. {storage_api.note}",
                                            storage_api.exc, self.run_util.log_enum.ERROR.value)
                self.health_caller.error(self.service_name, entry)

                # change run value in db 
                self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.STOPPED.value)
                
                # log the status change + health call
                self.run_util.log_status_change(self.service_name, self.run, self.status_enum.STOPPED.value)

                self.shut_down_due_to_failure()           
           
        return storage_api

    def shut_down_due_to_failure(self):        
        self.cons.close_connection()
        self.close_db_connections()
        print(f"{self.service_name} shutdown due to failure to contact 3rd party services.")
        time.sleep(5)
        os._exit(1)  # Exit the program with a non-zero status code to indicate an error

if __name__ == "__main__":
    HPCUnresponsiveJobHandler()