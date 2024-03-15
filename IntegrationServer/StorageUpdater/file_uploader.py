import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from MongoDB import mongo_connection
from StorageApi import storage_client
from Enums import validate_enum


"""
Responsible uploading files to open shares. 
"""

class FileUploader:

    def __init__(self):

        self.track_mongo = mongo_connection.MongoConnection("track")
        self.storage_api = storage_client.StorageClient()
        self.validate_enum = validate_enum.ValidateEnum
        
        self.run = True
        self.count = 2

        self.loop()

    def loop(self):

        while self.run:
            
            asset = self.track_mongo.get_entry_from_multiple_key_pairs([{"has_open_share" : self.validate_enum.YES.value, "has_new_files" : self.validate_enum.YES.value}])

            if asset is not None:
                guid = asset["_id"]
                
                
            

                time.sleep(1)

            if asset is None:
                time.sleep(1)

            self.count -= 1

            if self.count == 0:
                self.run = False


if __name__ == '__main__':
    FileUploader()