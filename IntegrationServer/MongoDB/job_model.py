from datetime import datetime

from IntegrationServer import utility


class JobModel:

    def __init__(self, guid, pipeline):
        self.util = utility.Utility()

        self._id = guid
        self.pipeline = pipeline
        self.pipeline_job_config_path = "./ConfigFiles/pipeline_job_config.json"
        self.job_list = self.create_joblist()

    def create_joblist(self):
        job_mapping = self.util.get_value(self.pipeline_job_config_path, self.pipeline)

        # Convert job_mapping to a list of dictionaries with additional fields
        job_list = []
        for job, label in job_mapping.items():
            job_entry = {
                "name": label,
                "status": "WAITING",  # Set default status
                "priority": (len(job_list) + 1),  # Set priority
                "timestamp": str(datetime.utcnow()),  # Default timestamp
                "slurm_job_id": -1,  # Default job ID
            }
            job_list.append(job_entry)

        return job_list

    def get_entry_data(self):
        entry_data = {
            "_id": self._id,
            "pipeline": self.pipeline,
            "job_list": self.job_list
        }
        return entry_data
