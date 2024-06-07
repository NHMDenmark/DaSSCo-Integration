from datetime import datetime
import time
import utility
from Enums import status_enum, validate_enum
from MongoDB.file_model import FileModel

"""
Model used when creating a new entry in the track collection. 
"""
class EntryModel:

    def __init__(self, guid, pipeline, derivative=False):
        self.util = utility.Utility()
        self.status = status_enum.StatusEnum

        self.pipeline_job_config_path = "/work/data/DaSSCo-Integration/IntegrationServer/ConfigFiles/pipeline_job_config.json"

        self._id = guid
        self.created_time = datetime.now() #datetime.utcnow()
        self.pipeline = pipeline
        self.batch_list_name = ""
        self.job_list = []
        if derivative is False:
            self.job_list = self.create_joblist()
        self.jobs_status = status_enum.StatusEnum.WAITING.value
        if derivative is True:
            self.jobs_status = status_enum.StatusEnum.DONE.value
        self.file_list = []
        self.files_status = status_enum.StatusEnum.NONE.value
        self.asset_size = -1
        self.proxy_path = ""
        self.hpc_ready = validate_enum.ValidateEnum.NO.value
        self.is_in_ars = validate_enum.ValidateEnum.AWAIT.value
        self.has_new_file = validate_enum.ValidateEnum.NO.value
        self.has_open_share = validate_enum.ValidateEnum.NO.value
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
                "job_queued_time": None, # Default timestamp
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
            "jobs_status": self.jobs_status,
            "file_list": self.file_list,
            "files_status": self.files_status,
            "asset_size": self.asset_size,
            "proxy_path": self.proxy_path,
            "hpc_ready": self.hpc_ready,
            "is_in_ars": self.is_in_ars,
            "has_new_file": self.has_new_file,
            "has_open_share": self.has_open_share,
            "erda_sync": self.erda_sync,
            "update_metadata": self.update_metadata
        }
        return entry_data
