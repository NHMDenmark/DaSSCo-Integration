from IntegrationServer.utility import Utility

""" 
Creates a _jobs.json file and assigns jobs based on pipeline for new files. 
"""


class JobAssigner:
    def __init__(self):
        self.util = Utility()
        self.pipeline_job_config_path = "../IntegrationServer/ConfigFiles/pipeline_job_config.json"

    def create_jobs(self, pipeline_name):
        try:
            config = self.util.get_value(self.pipeline_job_config_path, pipeline_name)

            jobs_dict = {}

            for key in config:
                job_name = config.get(key)
                jobs_dict[job_name] = "WAITING"

                order = key[4:]
                jobs_dict[order] = job_name

            return jobs_dict

        except Exception as e:
            print(f"Pipeline name does not match job in config file: {e}")
