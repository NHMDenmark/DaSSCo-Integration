from pydantic import BaseModel
from datetime import datetime

"""
Model class for the files added to the track entries.
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