import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from Enums import status_enum

""" 
Looks for the jobs in the job config file based on the pipeline name and creates and returns the list of jobs.  
"""

class JobAssigner:
    def __init__(self):
        self.util = utility.Utility()
        self.status = status_enum.StatusEnum
        self.pipeline_job_config_path = f"{project_root}/ConfigFiles/pipeline_job_config.json"

    def create_jobs(self, pipeline_name):
        try:
            config = self.util.get_value(self.pipeline_job_config_path, pipeline_name)

            jobs_dict = {}

            for key in config:
                job_name = config.get(key)
                jobs_dict[job_name] = self.status.WAITING.value

                order = key[4:]
                jobs_dict[order] = job_name

            return jobs_dict

        except Exception as e:
            print(f"Pipeline name likely does not match job in config file: {e}")
