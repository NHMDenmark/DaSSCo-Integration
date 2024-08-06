import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from MongoDB import track_repository
from Connections import connections
from Enums import status_enum, validate_enum
import utility
import time
from InformationModule.log_class import LogClass
from HealthUtility import health_caller

"""
Looks for assets that have been persisted with ARS and have not yet been created on the HPC cluster.
 
Connects through ssh to the hpc server and calls a script with guid, ARS link, batch id as parameters.
"""
# TODO Check that HPC is available. Get some status from mongo db. Other service responsible for updating that. 

class HPCAssetCreator(LogClass):

    def __init__(self):
        
        # setting up logging
        super().__init__(filename = f"{os.path.basename(os.path.abspath(__file__))}.log", name = os.path.relpath(os.path.abspath(__file__), start=project_root))
        # service name for logging/info purposes
        self.service_name = "Asset creator HPC"

        self.ssh_config_path = f"{project_root}/ConfigFiles/ucloud_connection_config.json"
        self.hpc_config_path = f"{project_root}/ConfigFiles/slurm_config.json"
        self.run_config_path = f"{project_root}/ConfigFiles/run_config.json"
        self.mongo_track = track_repository.TrackRepository()
        self.util = utility.Utility()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.cons = connections.Connections()

        # set the config file value to RUNNING, mostly for ease of testing
        self.util.update_json(self.run_config_path, self.service_name, self.status_enum.RUNNING.value)

        self.con = self.create_ssh_connection()

        self.run = self.util.get_value(self.run_config_path, self.service_name)        
        self.loop()

    def create_ssh_connection(self):
        self.cons.create_ssh_connection(self.ssh_config_path)
        # handle when connection wasnt established - calls health service and sets run config to STOPPED
        print(self.cons.exc)
        if self.cons.exc is not None:
            entry = self.log_exc(self.cons.msg, self.cons.exc, self.status_enum.ERROR.value)
            self.health_caller.warning(self.service_name, entry)
            self.util.update_json(self.run_config_path, self.service_name, self.status_enum.STOPPED.value)
        
        return self.cons.get_connection()

    def loop(self):

        while self.run == status_enum.StatusEnum.RUNNING.value:
            """
            if output != "alive":
                try:
                    self.cons.create_ssh_connection(self.ssh_config_path)
                    self.con = self.cons.get_connection()
                except Exception as e:
                    print(f"{e} : exception while reconnecting to hpc server")
                    time.sleep(60)
                    continue
            """
            asset = None
            asset = self.mongo_track.get_entry_from_multiple_key_pairs([{"hpc_ready": validate_enum.ValidateEnum.NO.value, "has_open_share": validate_enum.ValidateEnum.YES.value,
                                                                          "jobs_status": status_enum.StatusEnum.WAITING.value, "is_in_ars": validate_enum.ValidateEnum.YES.value,
                                                                            "has_new_file": validate_enum.ValidateEnum.NO.value, "erda_sync": validate_enum.ValidateEnum.YES.value}])
            if asset is None:
                #print("No asset found for creation on HPC")
                time.sleep(1)        
            else: 

                guid = asset["_id"]
                batch_id = asset["batch_list_name"]                
                files = asset["file_list"]

                link = None

                # TODO handle multiple files belonging to an asset
                for file in files:
                    link = file["ars_link"]
                # print(link)
                if link is not None:
                    script_path = self.util.get_value(self.hpc_config_path, "initiate_script")
                    # print(script_path)
                    self.mongo_track.update_entry(guid, "hpc_ready", validate_enum.ValidateEnum.AWAIT.value)
                    print(f"bash {script_path} {guid} {batch_id} {link}")
                    self.con.ssh_command(f"bash {script_path} {guid} {batch_id} {link}")
                # TODO handle if link is none - needs some kind of status update that there is a missing link or no files belonging to the asset
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


if __name__ == '__main__':
    HPCAssetCreator()
