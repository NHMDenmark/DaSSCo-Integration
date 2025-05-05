from enum import Enum
"""
Holds all the fields that can exist in the track database
"""
class TrackFieldsEnum(Enum):
    ID = "_id"
    CREATED_TIMESTAMP = "created_timestamp"
    PIPELINE = "pipeline"
    BATCH_LIST_NAME = "batch_list_name"
    JOB_LIST = "job_list"
    JOBS_STATUS = "jobs_status"
    FILE_LIST = "file_list"
    FILES_STATUS = "files_status"
    ASSET_SIZE = "asset_size"
    PROXY_PATH = "proxy_path"
    ASSET_TYPE = "asset_type"
    HPC_READY = "hpc_ready"
    IS_IN_ARS = "is_in_ars"
    HAS_NEW_FILE = "has_new_file"
    HAS_OPEN_SHARE = "has_open_share"
    ERDA_SYNC = "erda_sync"
    UPDATE_METADATA = "update_metadata"
    TEMPORARY_FILES_NDRIVE = "temporary_files_ndrive"
    TEMPORARY_PATH_NDRIVE = "temporary_path_ndrive"
    TEMPORARY_FILES_LOCAL = "temporary_files_local"
    TEMPORARY_PATH_LOCAL = "temporary_path_local"
    AVAILABLE_FOR_SERVICES = "available_for_services"
    AVAILABLE_FOR_SERVICES_TIMESTAMP = "available_for_services_timestamp"
    AVAILABLE_FOR_SERVICES_WAIT_TIME = "available_for_services_wait_time"

class TrackFields:
    def __init__(self):
        for field in TrackFieldsEnum:
            setattr(self, field.name, field.value)

class JobFieldsEnum(Enum):
    NAME = "name"
    STATUS = "status"
    PRIORITY = "priority"
    JOB_QUEUED_TIME = "job_queued_time"
    JOB_START_TIME = "job_start_time"
    HPC_JOB_ID = "hpc_job_id"

class JobFields:
    def __init__(self):
        for field in JobFieldsEnum:
            setattr(self, field.name, field.value)

class FileFieldsEnum(Enum):
    NAME = "name"
    TYPE = "type"
    TIME_ADDED = "time_added"
    CHECK_SUM = "check_sum"
    FILE_SIZE = "file_size"
    ARS_LINK = "ars_link"
    ERDA_SYNC = "erda_sync"
    DELETED = "deleted"

class FileFields:
    def __init__(self):
        for field in FileFieldsEnum:
            setattr(self, field.name, field.value)
