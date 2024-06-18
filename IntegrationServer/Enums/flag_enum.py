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
