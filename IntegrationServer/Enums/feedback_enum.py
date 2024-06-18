from enum import Enum

class FeedbackEnum(Enum):
    OK = "OK"
    FAIL = "FAIL"
    AWAIT = "AWAIT"

class Feedback():

    def __init__(self):
        
        self.FAIL = FeedbackEnum.FAIL.value
        self.AWAIT = FeedbackEnum.AWAIT.value
        self.OK = FeedbackEnum.OK.value
