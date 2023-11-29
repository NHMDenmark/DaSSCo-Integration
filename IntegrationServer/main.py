import os
from IntegrationServer.Connections import ssh
from IntegrationServer.Connections import connections
from IntegrationServer import utility
from IntegrationServer.JobList import job_driver
from IntegrationServer.FileStatus import status
from IntegrationServer.Connections import rest_api
import threading
import time


class IntegrationServer(object):
    def __init__(self):

        self.util = utility.Utility()
        self.jobby = job_driver.JobDriver()
        self.stat = status.TotalStatus()
        self.cons = connections.Connections()

        self.new_files_path = "./Files/NewFiles/"
        self.updated_files_path = "./Files/UpdatedFiles/"
        self.ssh_config_path = "ConfigFiles/ssh_connections_config.json"

        # flags to keep track of which threads are running
        self.flags = [False, False, False, False, False]

        self.cons.create_ssh_connections(self.ssh_config_path)

    def octopus(self):

        counter = 0
        running = True

        while running:

            print("Start loop")
            """
            if not self.flags[0]:
                self.flags[0] = True
                thread_one = threading.Thread(target=self.look_for_external_new_files)
                thread_one.start()

            if not self.flags[1]:
                self.flags[1] = True
                thread_two = threading.Thread(target=self.process_new_internal_files)
                thread_two.start()
            
            if not self.flags[2]:
                self.flags[2] = True
                thread_three = threading.Thread(target=self.look_for_external_updated_files)
                thread_three.start()
            """
            if not self.flags[3]:
                self.flags[3] = True
                thread_four = threading.Thread(target=self.process_updated_internal_files)
                thread_four.start()

            if not self.flags[4]:
                self.flags[4] = True
                thread_five = threading.Thread(target=self.send_files_to_pipes)
                thread_five.start()

            time.sleep(5)
            counter += 1

            if counter >= 4:
                self.cons.close_all()
                print("Shutting down")
                running = False

    def look_for_external_new_files(self):
        # TODO create check for which connections should be looked at
        for con in self.cons.get_connections():
            print(f"{con.name} is {con.status}")
            if con.new_import_directory_path is not None:
                con.import_and_sort_files(con.new_import_directory_path, self.new_files_path)

        self.flags[0] = False

    def process_new_internal_files(self):
        self.jobby.process_new_directories()

        self.flags[1] = False

    def look_for_external_updated_files(self):
        # TODO create check for which connections should be looked at
        for con in self.cons.get_connections():
            # print(f"{con.name} is {con.status}")
            con.import_and_sort_files(con.updated_import_directory_path, self.updated_files_path)

        self.flags[2] = False

    def process_updated_internal_files(self):

        self.jobby.process_updated_directories()

        self.flags[3] = False

    def send_files_to_pipes(self):

        print("starting send files to pipeline")

        capacity = 100  # get_slurm_capacity()

        transfer_filepath_list = {"./Files/InProcess/PIPEHERB0001/phb"}  # create_transfer_filelist(capacity)

        total_expected_time = 3  # get from above as well

        for con in self.cons.get_connections():

            if not con.is_slurm:
                continue

            for directory in transfer_filepath_list:
                con.sftp_export_directory_to_server(directory, con.export_directory_path)

            # con.ssh_command("ls")

        time.sleep(total_expected_time)  # not sure this works

        print(f"done sending to pipe after {total_expected_time}")

        self.flags[4] = False


def test():
    util = utility.Utility()
    jobby = job_driver.JobDriver()
    stat = status.TotalStatus()
    cons = connections.Connections()
    api = rest_api.APIUsage()

    """
    cons.create_ssh_connections("./ssh_connections_config.json")
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

    # con.ssh_command("ls")
    """

    api.get_bearer_token()
    # api.create_asset()
    api.update_asset()
    api.api_get_asset()

if __name__ == '__main__':
    # git rm -r --cached .idea/
    # i = IntegrationServer()
    # i.octopus()
    test()
