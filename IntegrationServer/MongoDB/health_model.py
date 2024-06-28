from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

"""
Model class for entries added  to the health collection.
"""

class HealthModel(BaseModel):
    service: Optional[str] = None
    timestamp: datetime = datetime.now()
    severity_level: str = "WARNING"
    message: Optional[str] = None
    guid: Optional[str] = None
    exception: Optional[str] = None
    flag: Optional[str] = None
    sent: Optional[str] = "NO"