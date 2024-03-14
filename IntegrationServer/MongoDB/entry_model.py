from datetime import datetime

import utility
from Enums import status_enum, validate_enum

class EntryModel:

    def __init__(self, guid, pipeline):
        self.util = utility.Utility()
        self.status = status_enum.StatusEnum

        self.pipeline_job_config_path = "IntegrationServer/ConfigFiles/pipeline_job_config.json"

        self._id = guid
        self.created_time = datetime.utcnow()
        self.pipeline = pipeline
        self.job_list = self.create_joblist()
        self.is_on_hpc = validate_enum.ValidateEnum.NO.value
        self.is_in_ars = validate_enum.ValidateEnum.NO.value
        self.jobs_status = status_enum.StatusEnum.WAITING.value
        self.ars_file_link = ""
        self.batch_list_name = ""
        self.image_check_sum = -1 # Default value
        self.erda_sync = validate_enum.ValidateEnum.NO.value
        self.update_metadata = validate_enum.ValidateEnum.NO.value


    def create_joblist(self):
        job_mapping = self.util.get_value(self.pipeline_job_config_path, self.pipeline)

        # Convert job_mapping to a list of dictionaries with additional fields
        job_list = []
        for job, label in job_mapping.items():
            job_entry = {
                "name": label,
                "status": self.status.WAITING.value,  # Set default status
                "priority": (len(job_list) + 1),  # Set priority
                "job_start_time": None,  # Default timestamp
                "hpc_job_id": -9,  # Default job ID, changed to -9 from -1 due to agreement with HPC scripts to use -1 as error when queueing
            }
            job_list.append(job_entry)

        return job_list

    # Used when creating a new entry
    def get_entry_data(self):
        entry_data = {
            "_id": self._id,
            "created_timestamp": self.created_time,
            "pipeline": self.pipeline,
            "batch_list_name": self.batch_list_name,
            "job_list": self.job_list,
            "is_on_hpc": self.is_on_hpc,
            "is_in_ars": self.is_in_ars,
            "jobs_status": self.jobs_status,
            "ars_file_link": self.ars_file_link,
            "image_check_sum": self.image_check_sum,
            "erda_sync": self.erda_sync,
            "update_metadata": self.update_metadata
        }
        return entry_data
