import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from Connections import connections
from MongoDB import mongo_connection
import utility
import time

"""
Responsible for transfering metadata files to slurm and updating mongodb when that has happened. 
"""

class SlurmTransfer:

    def __init__(self):

        self.ssh_config_path = "IntegrationServer/ConfigFiles/ucloud_connection_config.json"
        self.slurm_config_path = "IntegrationServer/ConfigFiles/slurm_config.json"

        self.run = True
        self.count = 2 

        self.cons = connections.Connections()
        self.util = utility.Utility()
        self.mongo_track = mongo_connection.MongoConnection("track")
        self.mongo_slurm = mongo_connection.MongoConnection("slurm")

        self.export_path = self.util.get_value(self.slurm_config_path, "export_to_path")

        self.cons.create_ssh_connection(self.ssh_config_path)
        self.con = self.cons.get_connection()

        self.loop()
    
    def loop(self):
        
        while self.run:
            discovered = False
            guid, asset_path, discovered = self.look_for_asset_not_on_slurm()

            transfered = False
            if discovered:
                transfered = self.transfer_asset_to_slurm(guid, asset_path)

            if transfered:
                self.update_mongo(guid)

            if discovered:
                time.sleep(1)
            else:
                time.sleep(2)           


            self.count -= 1

            if self.count == 0:
                self.run = False
                self.cons.close_connection()

    def look_for_asset_not_on_slurm(self):
        
        asset = self.mongo_track.get_entry("is_on_slurm", False)
        guid = ""
        asset_path = ""

        if asset is not None:
            guid = asset["_id"]

            if asset["batch_list_name"] is not None:
                batch_date = asset["batch_list_name"][-10:]

                asset_path = f"{project_root}/Files/InProcess/{asset["pipeline"]}/{batch_date}/{guid}/{guid}.json"    

            if asset["batch_list_name"] is None:
                asset_path = f"{project_root}/Files/InProcess/{asset["pipeline"]}/{guid}/{guid}.json"

            try:
                self.util.read_json(asset_path)
                return guid, asset_path, True

            except Exception as e:
                print(f"Error creating path for {guid}: {e}")
                
        return "", "", False

    def transfer_asset_to_slurm(self, guid, asset_path):
        
        batch_id = self.mongo_track.get_value_for_key(guid, "batch_list_name")
        
        exp_path = f"{self.export_path}/derivatives/{guid}/{guid}.json"
        
        if batch_id is None:
            self.con.sftp_create_directory(f"{self.export_path}/derivatives", guid)
        
        if batch_id is not None:
            exp_path = f"{self.export_path}/{batch_id}/{guid}/{guid}.json"
            exists = self.con.sftp_create_directory(self.export_path, batch_id)
            if exists:
                self.con.sftp_create_directory(f"{self.export_path}/{batch_id}", guid)

        value = self.con.sftp_copy_file(asset_path, exp_path)

        if value == True:
            return value
        else:
            print(f"Transfer error for {guid}: {value}")
            return False
        

    def update_mongo(self, guid):
        self.mongo_slurm.add_entry_to_list(guid, "is_on_slurm")
        self.mongo_track.update_entry(guid, "is_on_slurm", True)


if __name__ == '__main__':
    SlurmTransfer()