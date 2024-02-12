# from IntegrationServer.Connections import smb_connecter
# from IntegrationServer.Connections import connections
import utility
# from IntegrationServer.JobList import job_driver
# from IntegrationServer.Connections import northtech_rest_api
from MongoDB import mongo_connection
import ndrive_new_files
import process_files_from_ndrive

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
    new_files = process_files_from_ndrive.ProcessNewFiles()

    #  cons.create_ssh_connections("./ConfigFiles/ssh_connections_config.json")

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

    # relPath = "IntegrationServer/Files/NewFiles/7e8-1-08-08-2c-12-0-000-00-000-0be5f3-00000.json"
    # meta_mongo.create_metadata_entry(relPath, util.get_value(relPath, "asset_guid"))
    # print(meta_mongo.get_entry("_id", util.get_value(relPath, "asset_guid")))

    # print(util.calculate_sha256_checksum("IntegrationServer/Files/InProcess/PIPEHERB0001/2024-01-08/7e8-1-08-08-29-07-0-000-00-000-0439e4-00000/7e8-1-08-08-29-07-0-000-00-000-0439e4-00000.tif"))
    
    # print(util.calculate_sha256_checksum("Tests/checksum.txt"))
                                         
if __name__ == '__main__':
    # git rm -r --cached .idea/
    # i = IntegrationServer()
    test()
