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