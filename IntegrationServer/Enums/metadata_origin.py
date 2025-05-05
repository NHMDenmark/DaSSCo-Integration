from enum import Enum

class MetadataOriginEnum(Enum):

    NDRIVE = "NDRIVE"
    INGESTION_QUEUE = "INGESTION_QUEUE"
    UCLOUD_HPC = "UCLOUD_HPC"

class MetadataOrigin:
    def __init__(self):
        self.NDRIVE = MetadataOriginEnum.NDRIVE.value
        self.INGESTION_QUEUE = MetadataOriginEnum.INGESTION_QUEUE.value
        self.UCLOUD_HPC = MetadataOriginEnum.UCLOUD_HPC.value        
