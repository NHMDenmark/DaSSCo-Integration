import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from MongoDB import track_repository, service_repository
from Connections import connections
from Enums import status_enum, validate_enum
import utility
import time
from HealthUtility import health_caller, run_utility

"""
Looks for assets that have been persisted with ARS, exists on hpc server and had all their jobs done.
Connects through ssh to the hpc server and calls a clean up script with the asset guid as parameter.
Logs error and warnings and contacts the health service when any are found.
Updates the status of the asset in the track db. 
"""

class HPCCleanUp():

    def __init__(self):
        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        # service name for logging/info purposes
        self.service_name = "HPC clean up service"
        self.prefix_id = "Hcus"

        self.ssh_config_path = f"{project_root}/ConfigFiles/ucloud_connection_config.json"
        self.hpc_config_path = f"{project_root}/ConfigFiles/slurm_config.json"
    
        self.mongo_track = track_repository.TrackRepository()
        self.service_mongo = service_repository.ServiceRepository()
        self.util = utility.Utility()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum
        self.cons = connections.Connections()

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
            
            asset = None
            asset = self.mongo_track.get_entry_from_multiple_key_pairs([{"hpc_ready": validate_enum.ValidateEnum.YES.value, "erda_sync": validate_enum.ValidateEnum.YES.value,
                                                                          "jobs_status": status_enum.StatusEnum.DONE.value, "is_in_ars": validate_enum.ValidateEnum.YES.value}])
            if asset is None:
                print("No asset found")
                time.sleep(10)        
            else: 
                guid = asset["_id"]
                try:
                    script_path = self.util.get_value(self.hpc_config_path, "clean_up_script")
                except Exception as e:
                    time.sleep(60)
                    continue
            
                self.con.ssh_command(f"bash {script_path} {guid}")

                self.mongo_track.update_entry(guid, "hpc_ready", validate_enum.ValidateEnum.AWAIT.value)

                time.sleep(1)

            # checks if service should keep running           
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.validate_enum.PAUSED.value:
                self.run = self.run_util.pause_loop()

        # outside main while loop        
        self.mongo_track.close_connection()
        self.cons.close_connection()


if __name__ == '__main__':
    HPCCleanUp()