from enum import Enum

"""
Enums representing severity of events logged. 
"""
class LogEnum(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    TESTING = "TESTING"

class Log:
    def __init__(self):
        self.DEBUG = LogEnum.DEBUG.value
        self.INFO = LogEnum.INFO.value
        self.WARNING = LogEnum.WARNING.value
        self.ERROR = LogEnum.ERROR.value
        self.CRITICAL = LogEnum.CRITICAL.value
        self.TESTING = LogEnum.TESTING.value