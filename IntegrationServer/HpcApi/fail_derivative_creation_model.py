from pydantic import BaseModel, Field

class FailDerivativeCreationModel(BaseModel):
    guid: str
    ppi: int
    note: str = None