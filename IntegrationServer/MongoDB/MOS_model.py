from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

"""
Model class for the MOS table.
"""

class MOSModel(BaseModel):
    _id: str
    created: datetime = datetime.now()
    label: bool
    spid: str = "NOT_AVAILABLE"
    disposable_id: str
    unique_label_id: str
    label_connections: List[str]
    