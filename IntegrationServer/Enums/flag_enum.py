from enum import Enum

"""
Enums representing flags used for various tracking purposes. 
"""
# TODO work in progress, needs to be implemented everywhere
class FlagEnum(Enum):
    IS_IN_ARS = "is_in_ars"
    HAS_NEW_FILE = "has_new_file"
    ERDA_SYNC = "erda_sync"
    UPDATE_METADATA = "update_metadata"
    HPC_READY = "hpc_ready"
    HAS_OPEN_SHARE = "has_open_share"
    JOBS_STATUS = "jobs_status"
    FILES_STATUS = "files_status"
    AVAILABLE_FOR_SERVICES = "available_for_services"
    AVAILABLE_FOR_SERVICES_TIMESTAMP = "available_for_services_timestamp"
    AVAILABLE_FOR_SERVICES_WAIT_TIME = "available_for_services_wait_time"

class Flag:
    def __init__(self):
        self.IS_IN_ARS = FlagEnum.IS_IN_ARS.value
        self.HAS_NEW_FILE = FlagEnum.HAS_NEW_FILE.value
        self.ERDA_SYNC = FlagEnum.ERDA_SYNC.value
        self.UPDATE_METADATA = FlagEnum.UPDATE_METADATA.value
        self.HPC_READY = FlagEnum.HPC_READY.value
        self.HAS_OPEN_SHARE = FlagEnum.HAS_OPEN_SHARE.value
        self.JOBS_STATUS = FlagEnum.JOBS_STATUS.value
        self.FILES_STATUS = FlagEnum.FILES_STATUS.value
        self.AVAILABLE_FOR_SERVICES = FlagEnum.AVAILABLE_FOR_SERVICES.value
        self.AVAILABLE_FOR_SERVICES_TIMESTAMP = FlagEnum.AVAILABLE_FOR_SERVICES_TIMESTAMP.value
        self.AVAILABLE_FOR_SERVICES_WAIT_TIME = FlagEnum.AVAILABLE_FOR_SERVICES_WAIT_TIME.value