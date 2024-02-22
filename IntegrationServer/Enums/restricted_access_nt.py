from enum import Enum

class RestrictedAccessNT(Enum):
    DEVELOPER = "DEVELOPER"
    USER = "USER"
    SERVICE_USER = "SERVICE_USER"
    ADMIN = "ADMIN"