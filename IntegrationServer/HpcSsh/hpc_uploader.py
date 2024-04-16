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

        self.ssh_config_path = "IntegrationServer/ConfigFiles/ucloud_connection_config.json"
        self.job_detail_path = "IntegrationServer/ConfigFiles/job_detail_config.json"

        self.cons = connections.Connections()
        self.util = utility.Utility()

        self.cons.create_ssh_connection(self.ssh_config_path)
        self.con = self.cons.get_connection()

        self.mongo_track = mongo_connection.MongoConnection("track")
        self.mongo_metadata = mongo_connection.MongoConnection("metadata")

    def loop(self):

        while self.run:
            
            asset = None
            asset = self.mongo_track.get_entry_from_multiple_key_pairs([{"hpc_ready": validate_enum.ValidateEnum.NO.value, "has_open_share": validate_enum.ValidateEnum.YES.value,
                                                                          "jobs_status": status_enum.StatusEnum.DONE.value, "is_in_ars": validate_enum.ValidateEnum.YES.value,
                                                                            "has_new_file": validate_enum.ValidateEnum.YES.value, "erda_sync": validate_enum.ValidateEnum.NO.value}])
            if asset is None:
                print("No asset found")
                time.sleep(1)        
            else: 
                 
                guid = asset["_id"]
                
                
                    

            self.count -= 1

            if self.count == 0:
                self.run = False
                self.mongo_track.close_mdb()
                self.mongo_metadata.close_mdb()
                self.cons.close_connection()

if __name__ == '__main__':
    HPCUploader()