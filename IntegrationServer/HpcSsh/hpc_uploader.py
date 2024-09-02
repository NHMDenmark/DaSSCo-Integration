import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from MongoDB import track_repository, metadata_repository, service_repository
from Connections import connections
from Enums import status_enum, validate_enum
import utility
import time
from HealthUtility import health_caller, run_utility

class HPCUploader():

    def __init__(self):

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        # service name for logging/info purposes
        self.service_name = "HPC file uploader"
        self.prefix_id = "Hfu"

        self.ssh_config_path = f"{project_root}/ConfigFiles/ucloud_connection_config.json"
        self.job_detail_path = f"{project_root}/ConfigFiles/job_detail_config.json"
        self.slurm_config_path = f"{project_root}/ConfigFiles/slurm_config.json"
        
        self.util = utility.Utility()
        self.mongo_track = track_repository.TrackRepository()
        self.mongo_metadata = metadata_repository.MetadataRepository()
        self.service_mongo = service_repository.ServiceRepository()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum
        self.cons = connections.Connections()
        self.upload_file_script = self.util.get_value(self.slurm_config_path, "upload_file_script")

        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name)

        # set the service db value to RUNNING, mostly for ease of testing
        self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.RUNNING.value)

        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        self.con = self.create_ssh_connection()
        
        self.run = self.run_util.get_service_run_status()
        self.run_util.service_run = self.run
        
        self.loop()
    
    def create_ssh_connection(self):
        self.cons.create_ssh_connection(self.ssh_config_path)
        # handle when connection wasnt established - calls health service and sets run config to STOPPED
        if self.cons.exc is not None:
            entry = self.run_util.log_exc(self.prefix_id, self.cons.msg, self.cons.exc, self.status_enum.ERROR.value)
            self.health_caller.warning(self.service_name, entry)
            self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.STOPPED.value)
        
        return self.cons.get_connection()


    def loop(self):

        while self.run == status_enum.StatusEnum.RUNNING.value:
            
            asset = self.mongo_track.get_entry_from_multiple_key_pairs([{"hpc_ready": validate_enum.ValidateEnum.YES.value, "has_open_share": validate_enum.ValidateEnum.YES.value,
                                                                          "jobs_status": status_enum.StatusEnum.DONE.value, "is_in_ars": validate_enum.ValidateEnum.YES.value,
                                                                            "has_new_file": validate_enum.ValidateEnum.YES.value, "erda_sync": validate_enum.ValidateEnum.NO.value}])
            if asset is None:
                print("No asset found")
                time.sleep(1)        
            else: 
                 
                guid = asset["_id"]
                """
                These were used in earlier version as arguments for the script called on slurm specifically.
                proxy_path = asset["proxy_path"]
                pipeline = self.mongo_metadata.get_value_for_key(guid, "pipeline_name")
                collection = self.mongo_metadata.get_value_for_key(guid, "collection")
                """
                try:
                    self.con.ssh_command(f"bash {self.upload_file_script} {guid}")

                    self.mongo_track.update_entry(guid, "has_new_file", validate_enum.ValidateEnum.UPLOADING.value)


                except Exception as e:
                    pass # TODO handle exception
                
            # checks if service should keep running - configurable in ConfigFiles/run_config.json            
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.validate_enum.PAUSED.value:
                self.run = self.run_util.pause_loop()

        # outside main while loop        
        self.mongo_track.close_connection()
        self.mongo_metadata.close_connection()
        self.cons.close_connection()

if __name__ == '__main__':
    HPCUploader()