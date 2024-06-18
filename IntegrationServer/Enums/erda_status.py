from enum import Enum

class ErdaStatusEnum(Enum):
    COMPLETED = "COMPLETED"
    ASSET_RECEIVED = "ASSET_RECEIVED"
    METADATA_RECEIVED = "METADATA_RECEIVED"
    ERDA_ERROR = "ERDA_ERROR"

class ErdaStatus:
    def __init__(self):
        self.COMPLETED = ErdaStatusEnum.COMPLETED.value
        self.ASSET_RECEIVED = ErdaStatusEnum.ASSET_RECEIVED.value
        self.METADATA_RECEIVED = ErdaStatusEnum.METADATA_RECEIVED.value
        self.ERDA_ERROR = ErdaStatusEnum.ERDA_ERROR.value