import glob
import os

from IntegrationServer.Connections import connections
from IntegrationServer import utility
import time

"""
Slurm server job api. Connects through ssh to the slurm server. Runs an infinite loop that goes through pipeline 
directories and checks for jobs that are ready to be processed through slurm.
"""


class SlurmStarter:

    def __init__(self):

        self.ssh_config_path = "ConfigFiles/ucloud_connection_config.json"
        self.slurm_config_path = "ConfigFiles/slurm_config.json"
        self.job_details_config_path = "ConfigFiles/job_detail_config.json"
        self.pipeline_job_path = "ConfigFiles/pipeline_job_config.json"
        self.work_server_directory_path = "/work/dassco_23_request/lars"
        self.job_list_path = "job_list.txt"
        self.run = True
        self.count = 0

        self.test_job_script = "/work/dassco_23_request/lars/test_job.sh"

        self.cons = connections.Connections()
        self.util = utility.Utility()

        self.job_list_script = self.util.get_value(self.slurm_config_path, "job_list_script_path")

        self.cons.create_ssh_connection(self.ssh_config_path)
        self.con = self.cons.get_connection()

        self.loop()

    """
    Main loop for starting and controlling the flow of slurm jobs. Makes use of batch scripts within the slurm server,
    through a ssh connection to check status of and start new jobs. 
    Configurable settings for amount of jobs through slurm_config.json. This need to be setup correctly with the sbatch
    scripts on the slurm server though. 
    """

    def loop(self):

        while self.run:

            max_jobs = self.util.get_value(self.slurm_config_path, "max_queued_jobs")

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

                transfer_filepath_list, pipeline, job_name = self.create_transfer_filelist(number_of_jobs_to_add)

                job_script_path = self.util.get_nested_value(self.job_details_config_path, job_name, "script")

                number_of_jobs = number_of_jobs_to_add  # len(transfer_filepath_list) TODO change here from test number
                parallel_jobs = self.util.get_value(self.slurm_config_path, "parallel_jobs")
                # total_expected_time = 3  # TODO get from above as well, not sure we still want this. Can be incorporated much later if needed probably

                pipe_path = f"/{pipeline}"
                export_pipeline_path = self.con.export_directory_path + pipe_path

                self.con.ssh_command(f"mkdir -p {export_pipeline_path}")

                for path in transfer_filepath_list:
                    print(path, export_pipeline_path)
                    self.con.sftp_export_directory_to_server(path, export_pipeline_path)
                    export_dir_path = export_pipeline_path + "/" + os.path.basename(path)
                    self.con.sftp_check_files_are_transferred(path, export_dir_path)

                # TODO Need template for sbatch script that can figure out where files are or which job needs to be done.
                command = f"sbatch {job_script_path} {number_of_jobs} {parallel_jobs}"

                if job_script_path is not None:
                    print(command)
                    self.con.ssh_command(command)
                else:
                    print("No jobs to be done")

            time.sleep(4)

            self.count += 1

            if self.count > 1:
                self.run = False
                self.cons.close_connection()

    """
    Return a list of directories that can be transferred to the slurm server,
    the pipeline name and the specific job name.
    """

    def create_transfer_filelist(self, max_jobs_number):

        directory_path = "./Files/InProcess"

        data = self.util.read_json(self.pipeline_job_path)

        jobs = list(data.keys())

        for job in jobs:

            pipeline_path = os.path.join(directory_path, job)

            pipeline_asset_list = self.get_paths_in_directory(pipeline_path)

            if len(pipeline_asset_list) != 0:
                ready_job_paths, job_name = self.get_ready_job(pipeline_asset_list, max_jobs_number)

                return ready_job_paths, job, job_name

    """
    Returns a list of paths containing ready jobs from a specific pipeline of a specific type. Returns the specific job name. 
    Updates the status of the job to INPIPELINE from READY.
    Example could be HERBARIUMPIPELINE with jobs being LABEL. If there are more than one set of READY jobs,
    within a pipeline directory a second run through that pipeline directory will be made later.
    """

    def get_ready_job(self, path_list, max_jobs_number):
        file_pattern = '_jobs.json'

        transfer_list = []
        specific_job_name = None

        for path in path_list:

            if len(transfer_list) < max_jobs_number:

                files_list = self.get_paths_in_directory(path)
                for file in files_list:

                    try:
                        if file[-10:] == file_pattern:
                            dictionary = self.util.read_json(file)
                            ready = self.util.find_keys_with_value(dictionary, "READY")
                            used_job_name = ""

                            print(specific_job_name, ready)

                            if specific_job_name is None and len(ready) == 1:
                                specific_job_name = ready[0]
                                used_job_name = ready[0]
                            elif len(ready) > 1:
                                # TODO move to error folder
                                print("Too many ready jobs")
                            else:
                                if len(ready) == 1:
                                    used_job_name = ready[0]

                            if len(ready) != 0 and used_job_name == specific_job_name:
                                transfer_list.append(path)
                                # updates job from ready to inpipeline status TODO turn on again
                                # self.util.update_json(file, ready[0], "INPIPELINE")

                    except Exception as e:
                        # TODO move such directories to Error
                        print(f"No _job.json file: {e}")

        return transfer_list, specific_job_name

    """
    Helper method returning all paths within a directory.
    """

    def get_paths_in_directory(self, dir_path):

        items = os.listdir(dir_path)

        paths = [os.path.join(dir_path, item) for item in items]

        return paths


if __name__ == '__main__':
    SlurmStarter()
