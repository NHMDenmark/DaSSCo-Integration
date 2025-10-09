from typing import Optional, Dict
from pydantic import BaseModel

class Specimen(BaseModel):
    institution: str
    collection: str
    barcode: str
    specimen_pid: str
    preparation_types: list[str]
    specimen_id: Optional[int] = None
    role_restrictions: Optional[list[Dict[str, str]]] = []