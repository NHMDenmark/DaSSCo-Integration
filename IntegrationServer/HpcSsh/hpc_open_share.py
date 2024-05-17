import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from MongoDB import mongo_connection
from StorageApi import storage_client
from Enums import status_enum, validate_enum
import utility
import time

"""
Description
"""
# TODO Check that HPC is available. Get some status from mongo db. Other service responsible for updating that. 

class HPCOpenShare:

    def __init__(self):

        self.hpc_config_path = f"{project_root}/ConfigFiles/slurm_config.json"

        self.run = True
        self.count = 4

        self.util = utility.Utility()

        self.mongo_track = mongo_connection.MongoConnection("track")
        self.mongo_metadata = mongo_connection.MongoConnection("metadata")
        #self.storage_api = storage_client.StorageClient()

        self.loop()


    def loop(self):

        while self.run:
            
            asset = None
            asset = self.mongo_track.get_entry_from_multiple_key_pairs([{"hpc_ready": validate_enum.ValidateEnum.NO.value, "has_open_share": validate_enum.ValidateEnum.NO.value,
                                                                          "jobs_status": status_enum.StatusEnum.WAITING.value, "is_in_ars": validate_enum.ValidateEnum.YES.value,
                                                                            "has_new_file": validate_enum.ValidateEnum.NO.value, "erda_sync": validate_enum.ValidateEnum.YES.value}])
            if asset is None:
                print("No asset found")
                time.sleep(10)        
            else: 
                time.sleep(5) 
                guid = asset["_id"]
                print(guid)
                institution = self.mongo_metadata.get_value_for_key(guid, "institution")
                collection = self.mongo_metadata.get_value_for_key(guid, "collection")
                asset_size = self.mongo_track.get_value_for_key(guid, "asset_size")
                
                storage_api = storage_client.StorageClient()
                proxy_path = storage_api.open_share(guid, institution, collection, asset_size)
                
                if proxy_path is not False:

                    self.mongo_track.update_entry(guid, "proxy_path", proxy_path)
                    
                    # create links for all files in the asset
                    files = asset["file_list"]

                    for file in files:
                        if file["deleted"] is not True:
                            name = file["name"]
                            link = f"{proxy_path}{name}"
                            print(file)
                            self.mongo_track.update_track_file_list(guid, name, "ars_link", link)

                    
                    self.mongo_track.update_entry(guid, "has_open_share", validate_enum.ValidateEnum.YES.value)

                # TODO handle if proxy path is false
                    

            #self.count -= 1
            run_config_path = f"{project_root}/ConfigFiles/run_config.json"
            
            run = self.util.get_value(run_config_path, "run")
            if run == "False":
                self.run = False
                self.mongo_track.close_mdb()
                self.mongo_metadata.close_mdb()
            if self.count == 0:
                self.run = False
                self.mongo_track.close_mdb()
                self.mongo_metadata.close_mdb()


if __name__ == '__main__':
    HPCOpenShare()
