from datetime import datetime

import utility
from Enums import status_enum

class EntryModel:

    def __init__(self, guid, pipeline):
        self.util = utility.Utility()
        self.status = status_enum.StatusEnum

        self.pipeline_job_config_path = "IntegrationServer/ConfigFiles/pipeline_job_config.json"

        self._id = guid
        self.pipeline = pipeline
        self.job_list = self.create_joblist()
        self.is_on_hpc = False
        self.is_in_ars = True # TODO change to false when ars actually is implemented. Should be updated by the Api storage after asset has image uploaded.

    def create_joblist(self):
        job_mapping = self.util.get_value(self.pipeline_job_config_path, self.pipeline)

        # Convert job_mapping to a list of dictionaries with additional fields
        job_list = []
        for job, label in job_mapping.items():
            job_entry = {
                "name": label,
                "status": self.status.WAITING.value,  # Set default status
                "priority": (len(job_list) + 1),  # Set priority
                "timestamp": datetime.utcnow(),  # Default timestamp
                "hpc_job_id": -1,  # Default job ID
            }
            job_list.append(job_entry)

        return job_list

    def get_entry_data(self):
        entry_data = {
            "_id": self._id,
            "pipeline": self.pipeline,
            "job_list": self.job_list,
            "is_on_hpc": self.is_on_hpc,
            "is_in_ars": self.is_in_ars
        }
        return entry_data
