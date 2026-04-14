
class InvalidInputError(Exception):
    def __init__(self, message="Input contains illegal characters or is the wrong utf type."):
        self.message = message
        super().__init__(self.message)

class InvalidStatusError(Exception):
    def __init__(self, message="Status value is invalid. Status must be one of: RUNNING, STOPPED, PAUSED."):
        self.message = message
        super().__init__(self.message)

class DatabaseUpdateError(Exception):
    def __init__(self, message="Failed to update the database."):
        self.message = message
        super().__init__(self.message)

class ServiceFailedError(Exception):
    def __init__(self, message="The service failed to perform the requested action."):
        self.message = message
        super().__init__(self.message)