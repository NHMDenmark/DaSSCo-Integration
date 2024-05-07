from pydantic import BaseModel

class FileInfoModel(BaseModel):
    guid: str
    name: str
    type: str
    check_sum: int
    file_size: int
    