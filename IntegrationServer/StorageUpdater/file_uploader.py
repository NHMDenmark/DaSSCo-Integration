import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import mongo_connection
from StorageApi import storage_client
from Enums import validate_enum, status_enum
import utility

"""
Responsible uploading files to open shares. 
"""

class FileUploader:

    def __init__(self):

        self.track_mongo = mongo_connection.MongoConnection("track")
        self.metadata_mongo = mongo_connection.MongoConnection("metadata")
        self.storage_api = storage_client.StorageClient()
        self.validate_enum = validate_enum.ValidateEnum
        self.status_enum = status_enum.StatusEnum
        self.util = utility.Utility() 

        self.run = True
        self.count = 2

        self.loop()

    def loop(self):

        while self.run:
            
            asset = self.track_mongo.get_entry_from_multiple_key_pairs([{"has_open_share" : self.validate_enum.YES.value, "has_new_file" : self.validate_enum.YES.value, "jobs_status" : self.status_enum.WAITING.value}])

            if asset is not None:
                guid = asset["_id"]
                print(guid)
                metadata = self.metadata_mongo.get_entry("_id", guid)
                if asset["asset_size"] != -1:

                    asset_files = asset["file_list"]

                    for file in asset_files:
                        

                        if file["erda_sync"] == validate_enum.ValidateEnum.NO.value:
                            
                            type = file["type"]
                            size = file["file_size"]

                            root = "/work/data/DaSSCo-Integration/IntegrationServer"
                            file_path = root + "/Files/InProcess/" + asset["pipeline"] + "/" + asset["batch_list_name"][-10:] + "/" + guid + "/" + guid + "." + type
                            #print(os.access(file_path, os.F_OK), os.access(file_path, os.X_OK))
                            # C:\Users\tvs157\Desktop\VSC_projects\DaSSCo-Integration\IntegrationServer\Files\InProcess\ti-p1\2022-10-02\third0003\third0003.tif
                            #print(file_path)
                            storage_api = storage_client.StorageClient()
                            uploaded = storage_api.upload_file(guid, metadata["institution"], metadata["collection"], file_path, size)
                            print(f"file uploaded: {uploaded}")
                            if uploaded is True:
                                self.track_mongo.update_entry(guid, "erda_sync", self.validate_enum.NO.value)
                                self.track_mongo.update_entry(guid, "has_new_file", self.validate_enum.AWAIT.value)
            # TODO handle fails    
                time.sleep(3)

            if asset is None:
                time.sleep(10)
            run=True
            run_config_path = f"{project_root}/ConfigFiles/run_config.json"
            
            run = self.util.get_value(run_config_path, "run")
            print(run)
            if run == "False":
                self.run = False
                self.track_mongo.close_mdb()
                self.metadata_mongo.close_mdb()

            #self.count -= 1

            if self.count == 0:
                self.run = False
                self.track_mongo.close_mdb()
                self.metadata_mongo.close_mdb()

if __name__ == '__main__':
    FileUploader()
