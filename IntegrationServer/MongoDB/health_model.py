from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

"""
Model class for entries added  to the health collection.
"""

class HealthModel(BaseModel):
    service: Optional[str]
    timestamp: datetime = datetime.now()
    severity_level: str = "WARNING"
    message: Optional[str]
    guid: Optional[str] = None
    exception: Optional[str] = None
    flag: Optional[str] = None
