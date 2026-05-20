from enum import Enum

class KeycloakRolesEnum(Enum):
    DASSCOADMIN = "dassco-admin"
    SERVICEUSER = "service-user"
    DASSCODEVELOPER = "dassco-developer"
    DASSCOUSER = "dassco-user"

class KeycloakRoles():

    def __init__(self):
        
        self.DASSCOADMIN = KeycloakRolesEnum.DASSCOADMIN.value
        self.SERVICEUSER = KeycloakRolesEnum.SERVICEUSER.value
        self.DASSCODEVELOPER = KeycloakRolesEnum.DASSCODEVELOPER.value
        self.DASSCOUSER = KeycloakRolesEnum.DASSCOUSER.value