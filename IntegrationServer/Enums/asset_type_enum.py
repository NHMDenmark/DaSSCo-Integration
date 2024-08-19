from enum import Enum

class AssetTypeEnum(Enum):
    UNKNOWN = "UNKNOWN"
    DEVICE_TARGET = "DEVICE_TARGET"
    SPECIMEN = "SPECIMEN"
    LABEL = "LABEL"

class AssetType:
    def __init__(self):
        self.UNKNOWN = AssetTypeEnum.UNKNOWN.value
        self.DEVICE_TARGET = AssetTypeEnum.DEVICE_TARGET.value
        self.SPECIMEN = AssetTypeEnum.SPECIMEN.value
        self.LABEL = AssetTypeEnum.LABEL.value