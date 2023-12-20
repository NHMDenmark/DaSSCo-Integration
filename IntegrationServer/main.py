from IntegrationServer.Connections import smb_connecter
from IntegrationServer.Connections import connections
from IntegrationServer import utility
from IntegrationServer.JobList import job_driver
from IntegrationServer.Connections import northtech_rest_api
from IntegrationServer.MongoDB import mongo_connection
from IntegrationServer import ndrive_new_files

""""
Test area for the different processes. May contain deprecated information.
"""


class IntegrationServer(object):
    def __init__(self):
        self.util = utility.Utility()
        self.jobby = job_driver.JobDriver()
        self.stat = status.TotalStatus()
        self.cons = connections.Connections()

        self.new_files_path = "./Files/NewFiles/"
        self.updated_files_path = "./Files/UpdatedFiles/"
        self.ssh_config_path = "ConfigFiles/ssh_connections_config.json"

        self.cons.create_ssh_connections(self.ssh_config_path)


def test():
    util = utility.Utility()
    jobby = job_driver.JobDriver()
    cons = connections.Connections()
    api = northtech_rest_api.APIUsage()
    smb = smb_connecter.SmbConnecter()
    mongo = mongo_connection.MongoConnection("test")
    ndrive = ndrive_new_files.NdriveNewFilesFinder()

    #  cons.create_ssh_connections("./ConfigFiles/ssh_connections_config.json")
    """
    time.sleep(1)

    jobby.process_new_directories()
    jobby.process_updated_directories()
    """
    """
    for con in cons.get_connections():
        print(f"{con.name} is {con.status}")
        con.import_and_sort_files("C://Users/lars_/OneDrive/Desktop/NORTHTECH/testMove", "./Files/NewFiles/")
    """
    """
    for con in cons.get_connections():
        print(f"{con.name} is {con.status}")
        con.sftp_export_directory_to_server("./Files/InProcess/EXAMPLE/check", con.export_directory_path)
    """
    """
    time.sleep(1)
    cons.close_all()
    """
    """
    # con = ssh.SSHConnection("connection1", "localhost", 22, os.getenv("CONNECTION1_USER"), os.getenv("CONNECTION1_PWD"))
    # time.sleep(1)
    """
    """
    write_output_path = "C:/Users/lars_/PycharmProjects/NHMD-IntegrationServer/IntegrationServer/job_list.txt"

    for con in cons.get_connections():
        con.ssh_command("bash /work/dassco_23_request/lars/job_list.sh", write_output_path)
        con.close()
    """
    # api.get_bearer_token()
    # api.create_asset()
    # api.update_asset()
    # api.api_get_asset()

    #  smb.test_run()
    # jobby.process_new_directories()

    # mongo.update_entry("65786da6cc9fccb118e6a2e1", "funding", "shingle")
    # print(mongo.get_entry("institution", "NHMD"))


if __name__ == '__main__':
    # git rm -r --cached .idea/
    # i = IntegrationServer()
    test()
