import os

from IntegrationServer.Connections import connections
from IntegrationServer import utility
import time


class SlurmReceiver:

    def __init__(self):
        self.ssh_config_path = "ConfigFiles/ucloud_connection_config.json"
        self.slurm_config_path = "ConfigFiles/slurm_config.json"
        self.job_details_config_path = "ConfigFiles/job_detail_config.json"
        self.pipeline_job_path = "ConfigFiles/pipeline_job_config.json"
        self.work_server_directory_path = "/work/dassco_23_request/lars"
        self.run = True
        self.count = 0

        self.cons = connections.Connections()
        self.util = utility.Utility()

        self.cons.create_ssh_connection(self.ssh_config_path)
        self.con = self.cons.get_connection()
        self.loop()

    def loop(self):

        while self.run:

            # check for files in pick up folder

            # check no errors occurred in pipelines -> handle errors

            # import? updated data files and/or update local files -> move local to updated files

            # check for more pipeline jobs -> if none delete files in slurm dir/ if more move files and set flag


            time.sleep(4)

            self.count += 1

            if self.count > 1:
                self.run = False
                self.cons.close_connection()


if __name__ == '__main__':
    n = SlurmReceiver()
