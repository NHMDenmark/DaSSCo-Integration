from pydantic import ConfigDict
from field_validation import SafeModel

class FileInfoModel(SafeModel):
    guid: str
    name: str
    type: str
    check_sum: int
    file_size: int

    model_config = ConfigDict(extra='forbid')
    