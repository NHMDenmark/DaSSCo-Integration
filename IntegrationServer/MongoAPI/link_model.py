from pydantic import BaseModel
from typing import Optional, List

class FileLinksModel(BaseModel):
    file_links: Optional[List[str]]