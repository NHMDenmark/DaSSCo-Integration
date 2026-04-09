from pydantic import ConfigDict
from field_validation import SafeModel

class FailDerivativeCreationModel(SafeModel):
    guid: str
    ppi: int
    note: str = None

    model_config = ConfigDict(extra='forbid')