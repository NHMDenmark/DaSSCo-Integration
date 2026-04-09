from pydantic import ConfigDict
from field_validation import SafeModel

class PauseModel(SafeModel):
    service_name: str
    run_status: str
    pause_counter: int
    message: str

    model_config = ConfigDict(extra='forbid')