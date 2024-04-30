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

class HPCUploader:

    def __init__(self):

        self.ssh_config_path = "/work/data/DaSSCo-Integration/IntegrationServer/ConfigFiles/ucloud_connection_config.json"
        self.job_detail_path = "/work/data/DaSSCo-Integration/IntegrationServer/ConfigFiles/job_detail_config.json"
        self.slurm_config_path = "/work/data/DaSSCo-Integration/IntegrationServer/ConfigFiles/slurm_config.json"

        self.cons = connections.Connections()
        self.util = utility.Utility()

        self.upload_file_script = self.util.get_value(self.slurm_config_path, "upload_file_script")

        self.cons.create_ssh_connection(self.ssh_config_path)
        self.con = self.cons.get_connection()

        self.mongo_track = mongo_connection.MongoConnection("track")
        self.mongo_metadata = mongo_connection.MongoConnection("metadata")
        
        self.run = True
        self.count = 4
        self.loop()

    def loop(self):

        while self.run:
            
            asset = None
            asset = self.mongo_track.get_entry_from_multiple_key_pairs([{"hpc_ready": validate_enum.ValidateEnum.NO.value, "has_open_share": validate_enum.ValidateEnum.YES.value,
                                                                          "jobs_status": status_enum.StatusEnum.DONE.value, "is_in_ars": validate_enum.ValidateEnum.YES.value,
                                                                            "has_new_file": validate_enum.ValidateEnum.YES.value, "erda_sync": validate_enum.ValidateEnum.NO.value}])
            
            if asset is None:
                print("No asset found")
                time.sleep(10)        
            else: 
                 
                guid = asset["_id"]
                #proxy_path = asset["proxy_path"]
                
                #pipeline = self.mongo_metadata.get_value_for_key(guid, "pipeline_name")
                #collection = self.mongo_metadata.get_value_for_key(guid, "collection")

                try:
                    self.con.ssh_command(f"bash {self.upload_file_script} {guid}")
                    print(self.upload_file_script, guid)
                    self.mongo_track.update_entry(guid, "has_new_file", validate_enum.ValidateEnum.UPLOADING.value)


                except Exception as e:
                    pass # TODO handle exception
                
                time.sleep(3)
            
            run_config_path = f"{project_root}/ConfigFiles/run_config.json"
            
            self.run = self.util.get_value(run_config_path, "run")
            if self.run == "False":
                self.run = False
                self.mongo_track.close_mdb()
                self.mongo_metadata.close_mdb()
                self.cons.close_connection()

            #self.count -= 1

            if self.count == 0:
                self.run = False
                self.mongo_track.close_mdb()
                self.mongo_metadata.close_mdb()
                self.cons.close_connection()

if __name__ == '__main__':
    HPCUploader()
