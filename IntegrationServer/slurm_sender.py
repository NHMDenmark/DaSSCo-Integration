import glob
import os

from IntegrationServer.Connections import connections
from IntegrationServer import utility
import time


class SlurmSender:

    def __init__(self):

        self.ssh_config_path = "ConfigFiles/ssh_connections_config.json"
        self.slurm_config_path = "ConfigFiles/slurm_config.json"
        self.job_list_script = "/work/dassco_23_request/lars/job_list.sh"
        self.pipeline_job_path = "ConfigFiles/pipeline_job_config.json"
        self.home_server_directory_path = "/work/dassco_23_request/lars"
        self.job_list_path = "job_list.txt"
        self.run = True
        self.count = 0

        self.test_job_script = "/work/dassco_23_request/lars/test_job.sh"

        self.cons = connections.Connections()
        self.util = utility.Utility()
        self.cons.create_ssh_connection(self.ssh_config_path)
        self.con = self.cons.get_connection()

        self.loop()

    def loop(self):

        self.con.ssh_command(f"cd {self.home_server_directory_path}")

        while self.run:

            max_jobs = self.util.get_value(self.slurm_config_path, "max_queued_jobs")

            if not self.con.is_slurm:
                continue

            self.con.ssh_command(f"bash {self.job_list_script}", self.job_list_path)

            with open(self.job_list_path, 'r') as file:
                running_jobs = file.readline().strip()
                pending_jobs = file.readline().strip()

                running_jobs = int(running_jobs)
                pending_jobs = int(pending_jobs)

                current_jobs = running_jobs + pending_jobs

            current_jobs = int(current_jobs)

            if max_jobs > current_jobs:

                number_of_jobs_to_add = max_jobs - current_jobs

                # transfer_filepath_list = {"./Files/InProcess/PIPEHERB0001/phb"}  # create_transfer_filelist(jobs_to_add)

                transfer_filepath_list, job_name = self.create_transfer_filelist(number_of_jobs_to_add)

                test_job_path = self.test_job_script  # TODO needs to get based on job_name from job_detail_config.json
                number_of_jobs = number_of_jobs_to_add  # len(transfer_filepath_list)
                total_expected_time = 3  # TODO get from above as well

                for path in transfer_filepath_list:
                    print(path, self.con.export_directory_path)
                    self.con.sftp_export_directory_to_server(path, self.con.export_directory_path)
                    # TODO change job status for paths copied

                command = f"sbatch {test_job_path} {number_of_jobs}"
                print(command)
                self.con.ssh_command(command)
                self.con.ssh_command("ls")

            time.sleep(3)

            self.count += 1

            if self.count > 1:
                self.run = False
                self.cons.close_all()

    def create_transfer_filelist(self, max_jobs_number):

        # ready_list = look_through_files in pipeline and_find_READY_jobs()
        # final_list = loop through ready_list add job time until max_hours / number_of_jobs
        # return final_list

        directory_path = "./Files/InProcess"

        data = self.util.read_json(self.pipeline_job_path)

        jobs = list(data.keys())

        for job in jobs:

            pipeline_path = os.path.join(directory_path, job)

            pipeline_asset_list = self.get_paths_in_directory(pipeline_path)

            if len(pipeline_asset_list) != 0:
                ready_job_paths = self.get_ready_job(pipeline_asset_list, max_jobs_number)

                return ready_job_paths, job

    def get_ready_job(self, path_list, max_jobs_number):
        file_pattern = '_jobs.json'

        transfer_list = []

        for path in path_list:

            if len(transfer_list) < max_jobs_number:

                files_list = self.get_paths_in_directory(path)
                for file in files_list:

                    try:
                        if file[-10:] == file_pattern:
                            dictionary = self.util.read_json(file)
                            ready = self.util.find_keys_with_value(dictionary, "READY")

                            if len(ready) != 0:
                                transfer_list.append(path)

                    except Exception as e:
                        # TODO move such directories to Error
                        print(f"No _job.json file: {e}")

        return transfer_list

    def get_paths_in_directory(self, dir_path):

        items = os.listdir(dir_path)

        paths = [os.path.join(dir_path, item) for item in items]

        return paths


if __name__ == '__main__':
    n = SlurmSender()
