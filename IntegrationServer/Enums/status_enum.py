from enum import Enum

class StatusEnum(Enum):
    DONE = "DONE"
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    STARTING = "STARTING"
    ERROR = "ERROR"
    NONE = "NONE"
    QUEUED = "QUEUED"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    TESTING = "TESTING"
    CRITICAL_ERROR = "CRITICAL_ERROR"
    RETRY = "RETRY"
    FAILED = "FAILED"

class Status:
    def __init__(self):
        self.DONE = StatusEnum.DONE.value
        self.WAITING = StatusEnum.WAITING.value
        self.RUNNING = StatusEnum.RUNNING.value
        self.STARTING = StatusEnum.STARTING.value
        self.ERROR = StatusEnum.ERROR.value
        self.NONE = StatusEnum.NONE.value
        self.QUEUED = StatusEnum.QUEUED.value
        self.PAUSED = StatusEnum.PAUSED.value
        self.STOPPED = StatusEnum.STOPPED.value
        self.TESTING = StatusEnum.TESTING.value
        self.CRITICAL_ERROR = StatusEnum.CRITICAL_ERROR.value
        self.RETRY = StatusEnum.RETRY.value
        self.FAILED = StatusEnum.FAILED.value