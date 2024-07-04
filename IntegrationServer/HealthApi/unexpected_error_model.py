from pydantic import BaseModel

class UnexpectedErrorModel(BaseModel):
    service_name: str
    message: str