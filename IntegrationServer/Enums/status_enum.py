from enum import Enum

class StatusEnum(Enum):
    DONE = "DONE"
    WAITING = "WAITING"
    INPIPELINE = "INPIPELINE"
    ERROR = "ERROR"