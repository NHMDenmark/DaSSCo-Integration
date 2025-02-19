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
# TODO Responsible for checking availability on slurm. Will have to wait for later to be made. For now assuming there always is capacity. 
"""
# This is not in use
class HPCAvailability:

    def __init__(self):

        self.ssh_config_path = f"{project_root}/ConfigFiles/ucloud_connection_config.json"
        self.slurm_config_path = f"{project_root}/ConfigFiles/slurm_config.json"
        self.job_list_path = "job_list.txt"

        self.run = True
        self.count = 2

        self.cons = connections.Connections()
        self.util = utility.Utility()
        self.mongo_availability = mongo_connection.MongoConnection("availability")

        self.cons.create_ssh_connection(self.ssh_config_path)
        self.con = self.cons.get_connection()

        try:
            self.loop()
        except Exception as e:
            print("service crashed", e)
    
    def loop(self):
        
        while self.run:
            
            has_no_availability = False

            slurm_config_data = self.util.read_json(self.slurm_config_path)

            max_time = slurm_config_data["max_expected_time"]
            max_jobs = slurm_config_data["max_queued_jobs"]
            parallel_jobs = slurm_config_data["parallel_jobs"]

            self.con.ssh_command(f"bash {self.job_list_script}", self.job_list_path)

            """
            max_jobs = self.util.get_value(self.slurm_config_path, "max_queued_jobs")

            self.con.ssh_command(f"bash {self.job_list_script}", self.job_list_path)

            with open(self.job_list_path, 'r') as file:
                running_jobs = file.readline().strip()
                pending_jobs = file.readline().strip()

                running_jobs = int(running_jobs)
                pending_jobs = int(pending_jobs)

                current_jobs = running_jobs + pending_jobs

            current_jobs = int(current_jobs)
            
                # TODO Need template for sbatch script that can figure out where files are or which job needs to be done.
                command = f"sbatch {job_script_path} {number_of_jobs} {parallel_jobs}"
            """

            time.sleep(3)

            if has_no_availability:
                time.sleep(300)

            self.count -= 1

            if self.count == 0:
                self.run = False
                self.cons.close_connection()


if __name__ == '__main__':
    HPCAvailability()