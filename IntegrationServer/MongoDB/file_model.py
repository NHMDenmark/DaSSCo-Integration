from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

"""
Model class for the files (belonging to an asset) added to the track entries.
"""

class FileModel(BaseModel):
    name: str = ""
    type: str = ""
    time_added: datetime = datetime.now()
    check_sum: int = 0
    file_size: int = -1
    ars_link: str = ""
    erda_sync: str = ""
    deleted: bool = False