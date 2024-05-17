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

        self.ssh_config_path = "/work/data/DaSSCo-Integration/IntegrationServer/ConfigFiles/ucloud_connection_config.json"
        self.hpc_config_path = "/work/data/DaSSCo-Integration/IntegrationServer/ConfigFiles/slurm_config.json"
        

        self.run = True
        self.count = 4

        self.cons = connections.Connections()
        self.util = utility.Utility()

        self.cons.create_ssh_connection(self.ssh_config_path)
        self.con = self.cons.get_connection()

        self.mongo_track = mongo_connection.MongoConnection("track")

        self.loop()


    def loop(self):

        while self.run:
            output = "dead"
            output = self.con.ssh_command("echo alive")
            
            if output != "alive":
                try:
                    self.cons.create_ssh_connection(self.ssh_config_path)
                    self.con = self.cons.get_connection()
                except Exception as e:
                    print(f"{e} : exception while reconnecting to hpc server")
                    time.sleep(60)
                    continue

            asset = None
            asset = self.mongo_track.get_entry_from_multiple_key_pairs([{"hpc_ready": validate_enum.ValidateEnum.NO.value, "has_open_share": validate_enum.ValidateEnum.YES.value,
                                                                          "jobs_status": status_enum.StatusEnum.WAITING.value, "is_in_ars": validate_enum.ValidateEnum.YES.value,
                                                                            "has_new_file": validate_enum.ValidateEnum.NO.value, "erda_sync": validate_enum.ValidateEnum.YES.value}])
            if asset is None:
                print("No asset found")
                time.sleep(10)        
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

                    self.con.ssh_command(f"bash {script_path} {guid} {batch_id} {link}")
                
                time.sleep(3)

            #self.count -= 1
            run_config_path = f"{project_root}/ConfigFiles/run_config.json"
            
            run = self.util.get_value(run_config_path, "run")
            if run == "False":
                self.run = False
                self.cons.close_connection()
            if self.count == 0:
                self.run = False
                self.cons.close_connection()


if __name__ == '__main__':
    HPCAssetCreator()
