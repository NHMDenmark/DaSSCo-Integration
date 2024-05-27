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

class HPCAssetCreator:

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
            asset = self.mongo_track.get_entry_from_multiple_key_pairs([{"hpc_ready": validate_enum.ValidateEnum.NO.value, "has_open_share": validate_enum.ValidateEnum.YES.value,
                                                                          "jobs_status": status_enum.StatusEnum.WAITING.value, "is_in_ars": validate_enum.ValidateEnum.YES.value,
                                                                            "has_new_file": validate_enum.ValidateEnum.NO.value, "erda_sync": validate_enum.ValidateEnum.YES.value}])
            if asset is None:
                print("No asset found for creation on HPC")
                time.sleep(1)        
            else: 

                guid = asset["_id"]
                batch_id = asset["batch_list_name"]                
                files = asset["file_list"]

                link = None

                # TODO handle multiple files belonging to an asset
                for file in files:
                    link = file["ars_link"]

                if link is not None:
                    script_path = self.util.get_value(self.hpc_config_path, "initiate_script")

                    self.mongo_track.update_entry(guid, "hpc_ready", validate_enum.ValidateEnum.AWAIT.value)

                    self.con.ssh_command(f"bash {script_path} {guid} {batch_id} {link}", "C:/Users/tvs157/Desktop/VSC_projects/DaSSCo-Integration/postman.txt")
                # TODO handle if link is none - needs some kind of status update that there is a missing link or no files belonging to the asset
                time.sleep(1)


            # checks if service should keep running - configurable in ConfigFiles/run_config.json
            run_config_path = f"{project_root}/ConfigFiles/run_config.json"
            
            all_run = self.util.get_value(run_config_path, "all_run")
            service_run = self.util.get_value(run_config_path, "hpc_asset_creator_run")

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
    HPCAssetCreator()
