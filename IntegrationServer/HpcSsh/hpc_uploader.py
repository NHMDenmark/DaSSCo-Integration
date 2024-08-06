import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from MongoDB import track_repository, metadata_repository
from Connections import connections
from Enums import status_enum, validate_enum
import utility
import time
from HealthUtility import health_caller
from InformationModule.log_class import LogClass


class HPCUploader(LogClass):

    def __init__(self):

        # setting up logging
        super().__init__(filename = f"{os.path.basename(os.path.abspath(__file__))}.log", name = os.path.relpath(os.path.abspath(__file__), start=project_root))
        # service name for logging/info purposes
        self.service_name = "HPC file uploader"

        self.ssh_config_path = f"{project_root}/ConfigFiles/ucloud_connection_config.json"
        self.job_detail_path = f"{project_root}/ConfigFiles/job_detail_config.json"
        self.slurm_config_path = f"{project_root}/ConfigFiles/slurm_config.json"
        self.run_config_path = f"{project_root}/ConfigFiles/run_config.json"
        self.util = utility.Utility()
        self.mongo_track = track_repository.TrackRepository()
        self.mongo_metadata = metadata_repository.MetadataRepository()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.cons = connections.Connections()
        self.upload_file_script = self.util.get_value(self.slurm_config_path, "upload_file_script")

        # set the config file value to RUNNING, mostly for ease of testing
        self.util.update_json(self.run_config_path, self.service_name, self.status_enum.RUNNING.value)

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
            
            asset = self.mongo_track.get_entry_from_multiple_key_pairs([{"hpc_ready": validate_enum.ValidateEnum.NO.value, "has_open_share": validate_enum.ValidateEnum.YES.value,
                                                                          "jobs_status": status_enum.StatusEnum.DONE.value, "is_in_ars": validate_enum.ValidateEnum.YES.value,
                                                                            "has_new_file": validate_enum.ValidateEnum.YES.value, "erda_sync": validate_enum.ValidateEnum.NO.value}])
            
            if asset is None:
                #print("No asset found")
                time.sleep(10)        
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
        self.mongo_metadata.close_connection()
        self.cons.close_connection()

if __name__ == '__main__':
    HPCUploader()
