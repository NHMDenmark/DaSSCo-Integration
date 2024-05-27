import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from MongoDB import mongo_connection
from Connections import connections
from Enums import status_enum, validate_enum
import utility
import time

"""
Looks for assets that have been persisted with ARS and have not yet been created on the HPC cluster.
 
Connects through ssh to the hpc server and calls a script with guid, ARS link, batch id as parameters.
"""
# TODO Check that HPC is available. Get some status from mongo db. Other service responsible for updating that. 

class HPCCleanUp:

    def __init__(self):

        self.ssh_config_path = f"{project_root}/ConfigFiles/ucloud_connection_config.json"
        self.hpc_config_path = f"{project_root}/ConfigFiles/slurm_config.json"

        self.run = True
        self.count = 2

        self.cons = connections.Connections()
        self.util = utility.Utility()

        self.cons.create_ssh_connection(self.ssh_config_path)
        self.con = self.cons.get_connection()

        self.mongo_track = mongo_connection.MongoConnection("track")

        self.loop()


    def loop(self):

        while self.run:
            
            asset = None
            asset = self.mongo_track.get_entry_from_multiple_key_pairs([{"hpc_ready": validate_enum.ValidateEnum.YES.value,
                                                                          "jobs_status": status_enum.StatusEnum.DONE.value, "is_in_ars": validate_enum.ValidateEnum.YES.value}])
            if asset is None:
                print("No asset found")
                time.sleep(1)        
            else: 
                guid = asset["_id"]
                script_path = self.hpc_config_path["clean_up_script"]

                self.mongo_track.update_entry(guid, "hpc_ready", validate_enum.ValidateEnum.NO.value)

                self.con.ssh_command(f"bash {script_path} {guid}")

                time.sleep(1)

            # checks if service should keep running - configurable in ConfigFiles/run_config.json
            run_config_path = f"{project_root}/ConfigFiles/run_config.json"
            
            all_run = self.util.get_value(run_config_path, "all_run")
            service_run = self.util.get_value(run_config_path, "hpc_clean_up_run")

            if all_run == "False" or service_run == "False":
                self.run = False
                self.mongo_track.close_mdb()
                self.cons.close_connection()

            self.count -= 1

            if self.count == 0:
                self.run = False
                self.cons.close_connection()
                self.mongo_track.close_mdb()

if __name__ == '__main__':
    HPCCleanUp()