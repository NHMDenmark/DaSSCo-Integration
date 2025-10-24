from typing import Optional, Dict
from pydantic import BaseModel

class SpecimenModel(BaseModel):
    institution: Optional[str] = None
    collection: Optional[str] = None
    barcode: Optional[str] = None
    specimen_pid: Optional[str] = None
    preparation_types: Optional[list[str]] = []
    specimen_id: Optional[int] = None
    role_restrictions: Optional[list[Dict[str, str]]] = []