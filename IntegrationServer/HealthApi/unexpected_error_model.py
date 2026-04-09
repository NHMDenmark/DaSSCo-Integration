from pydantic import ConfigDict
from field_validation import SafeModel

class UnexpectedErrorModel(SafeModel):
    service_name: str
    message: str

    model_config = ConfigDict(extra='forbid')