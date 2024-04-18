from enum import Enum

class StatusEnum(Enum):
    DONE = "DONE"
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    STARTING = "STARTING"
    ERROR = "ERROR"
    NONE = "NONE"
    QUEUED = "QUEUED"