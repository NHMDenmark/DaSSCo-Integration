from enum import Enum

class ValidateEnum(Enum):
    YES = "YES"
    AWAIT = "AWAIT"
    UPLOADING = "UPLOADING"
    NO = "NO"
    PAUSED = "PAUSED"
    ERROR = "ERROR"
    CRITICAL_ERROR = "CRITICAL_ERROR"

class Validate:
    def __init__(self):
        self.YES = ValidateEnum.YES.value
        self.AWAIT = ValidateEnum.AWAIT.value
        self.UPLOADING = ValidateEnum.UPLOADING.value
        self.NO = ValidateEnum.NO.value
        self.PAUSED = ValidateEnum.PAUSED.value
        self.ERROR = ValidateEnum.ERROR.value
        self.CRITICAL_ERROR = ValidateEnum.CRITICAL_ERROR.value