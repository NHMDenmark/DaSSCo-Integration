from pydantic import ConfigDict
from field_validation import SafeModel

class RunStatusChangeModel(SafeModel):
    service_name: str
    run_status: str
    message: str

    model_config = ConfigDict(extra='forbid')