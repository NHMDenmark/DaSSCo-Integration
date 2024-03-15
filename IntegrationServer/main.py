# from IntegrationServer.Connections import smb_connecter
# from IntegrationServer.Connections import connections
import os
import utility
# from IntegrationServer.JobList import job_driver
# from IntegrationServer.Connections import northtech_rest_api
from MongoDB import mongo_connection
import IntegrationServer.Ndrive.ndrive_new_files as ndrive_new_files
import IntegrationServer.Ndrive.process_files_from_ndrive as process_files_from_ndrive
from StorageApi import storage_client
from HpcSsh import hpc_job_caller, hpc_asset_creator

""""
Test area for the different processes. May contain deprecated information.
"""


class IntegrationServer(object):
    def __init__(self):
        self.util = utility.Utility()
        # self.jobby = job_driver.JobDriver()
        # self.cons = connections.Connections()

        self.new_files_path = "IntegrationServer/Files/NewFiles/"
        self.updated_files_path = "IntegrationServer/Files/UpdatedFiles/"
        self.ssh_config_path = "IntegrationServer/ConfigFiles/ssh_connections_config.json"

        self.cons.create_ssh_connections(self.ssh_config_path)


def test():
    util = utility.Utility()
    # jobby = job_driver.JobDriver()
    # cons = connections.Connections()
    # api = northtech_rest_api.APIUsage()
    # smb = smb_connecter.SmbConnecter()
    # mongo = mongo_connection.MongoConnection("track")
    # meta_mongo = mongo_connection.MongoConnection("metadata")
    # ndrive = ndrive_new_files.NdriveNewFilesFinder()
    # new_files = process_files_from_ndrive.ProcessNewFiles()
    # ars = storage_client.StorageClient()
    # job_caller = hpc_job_caller.HPCJobCaller()
    # hpc_creator = hpc_asset_creator.HPCAssetCreator()
    #  cons.create_ssh_connections("./ConfigFiles/ssh_connections_config.json")
    storage = storage_client.StorageClient()

    #storage.test()
    print(storage.create_asset("third0003"))
    #storage.update_metadata("second0002", "Shorty")
    #print(storage.sync_erda("second0002"))
    #print(storage.get_asset_status("second0002"))
    #print(storage.open_share("second0002", "test-institution", "test-collection", 610))
    # api.get_bearer_token()
    # api.create_asset()
    # api.update_asset()
    # api.api_get_asset()

    #  smb.test_run()
    # jobby.process_new_directories()
 
    # mongo.update_entry("exa", "funding", "bringle")
    # mongo.create_track_entry("exa", "EXAMPLE")
    # mongo.update_track_job_status("7e8-1-08-08-29-07-0-000-00-000-03158e-00000", "label", "FULLPATH")
    # print(mongo.get_entry("_id", "exa"))
    # mongo.delete_entry("exa")

    relPath = "IntegrationServer/Files/NewFiles/test.json"
    # meta_mongo.create_metadata_entry(relPath, util.get_value(relPath, "asset_guid"))
    # print(meta_mongo.get_entry("_id", util.get_value(relPath, "asset_guid")))
    
    # print(util.calculate_sha256_checksum("IntegrationServer/Files/InProcess/PIPEHERB0001/2024-01-08/7e8-1-08-08-29-07-0-000-00-000-0439e4-00000/7e8-1-08-08-29-07-0-000-00-000-0439e4-00000.tif"))
    
    # print(util.calculate_sha256_checksum("Tests/checksum.txt"))
    # ars.test()
    """
    x = mongo.find_running_jobs_older_than()
    for entry in x:
        util.write_full_json(relPath, entry)
    
    crc = util.calculate_crc_checksum("C:/Users/tvs157/Desktop/VSC_projects/DaSSCo-Integration/postman.txt")
    """
    #mb = util.calculate_file_size_round_to_next_mb("C:/Users/tvs157/Desktop/CP0002637_L_selago_Fuji_ICC.tif")
    #print(mb)
    

if __name__ == '__main__':
    # git rm -r --cached .idea/
    # i = IntegrationServer()
    test()
    