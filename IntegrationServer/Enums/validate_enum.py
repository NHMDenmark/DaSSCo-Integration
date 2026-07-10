from enum import Enum

class ValidateEnum(Enum):
    YES = "YES"
    AWAIT = "AWAIT"
    UPLOADING = "UPLOADING"
    NO = "NO"
    PAUSED = "PAUSED"
    PREPARE = "PREPARE"
    ERROR = "ERROR"
    CRITICAL_ERROR = "CRITICAL_ERROR"
    TRUE = "TRUE"
    FALSE = "FALSE"
    ACTIVATE = "ACTIVATE"
    FORCE = "FORCE"
    REMOVED = "REMOVED"

class Validate:
    def __init__(self):
        self.YES = ValidateEnum.YES.value
        self.AWAIT = ValidateEnum.AWAIT.value
        self.UPLOADING = ValidateEnum.UPLOADING.value
        self.NO = ValidateEnum.NO.value
        self.PAUSED = ValidateEnum.PAUSED.value
        self.PREPARE = ValidateEnum.PREPARE.value
        self.ERROR = ValidateEnum.ERROR.value
        self.CRITICAL_ERROR = ValidateEnum.CRITICAL_ERROR.value
        self.TRUE = ValidateEnum.TRUE.value
        self.FALSE = ValidateEnum.FALSE.value
        self.ACTIVATE = ValidateEnum.ACTIVATE.value
        self.FORCE = ValidateEnum.FORCE.value
        self.REMOVED = ValidateEnum.REMOVED.value