from enum import Enum

class RestrictedAccessNT(Enum):
    DEVELOPER = "DEVELOPER"
    USER = "USER"
    SERVICE_USER = "SERVICE_USER"
    ADMIN = "ADMIN"

class RestrictedAccess:
    def __init__(self):
        self.DEVELOPER = RestrictedAccessNT.DEVELOPER.value
        self.USER = RestrictedAccessNT.USER.value
        self.SERVICE_USER = RestrictedAccessNT.SERVICE_USER.value
        self.ADMIN = RestrictedAccessNT.ADMIN.value