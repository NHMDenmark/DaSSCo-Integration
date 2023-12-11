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
        self.updated_files_path = "Files/UpdatedFiles"
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
            remote_import_dir = self.con.updated_import_directory_path
            remote_pipeline_paths = []
            try:
                # List directories in the import folder
                remote_pipeline_names = self.con.sftp.listdir(remote_import_dir)

                # Construct full paths for each remote pipeline
                for remote_pipe_name in remote_pipeline_names:
                    remote_pipe_name = "/" + remote_pipe_name
                    remote_pipeline_path = remote_import_dir + remote_pipe_name
                    remote_pipeline_paths.append(remote_pipeline_path)

                for pipeline_path in remote_pipeline_paths:
                    # List directories in the pipeline path this is giving me the error
                    remote_guid_name_dirs = self.con.sftp.listdir(pipeline_path)

                    remote_guid_name_paths = []

                    # Construct full paths for each remote GUID directory
                    for remote_guid_name_dir in remote_guid_name_dirs:
                        remote_guid_name_dir = "/" + remote_guid_name_dir
                        remote_guid_name_path = pipeline_path + remote_guid_name_dir
                        remote_guid_name_paths.append(remote_guid_name_path)

                    # Transfer each GUID directory to the local path
                    for guid_path in remote_guid_name_paths:
                        import_path = os.path.join(self.updated_files_path, os.path.basename(guid_path))
                        self.con.sftp_import_directory_from_server(guid_path, import_path)

            except Exception as e:
                print(f"Error: {e}")

            # check no errors occurred in pipelines -> handle errors

            # import? updated data files and/or update local files -> move local to updated files
            # update job status

            # check for more pipeline jobs -> if none delete files in slurm dir/ if more move files and set flag

            time.sleep(1)

            self.count += 1

            if self.count > 1:
                self.run = False
                self.cons.close_connection()


if __name__ == '__main__':
    SlurmReceiver()
