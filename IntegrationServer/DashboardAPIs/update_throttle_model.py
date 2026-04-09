from typing import Optional
from field_validation import SafeModel
from pydantic import ConfigDict

class UpdateThrottleModel(SafeModel):
    assets_in_flight: Optional[int] = 0
    await_specify_sync_count: Optional[int] = 0
    await_sync_asset_count: Optional[int] = 0
    total_asset_size_mb: Optional[int] = 0
    total_reopened_share_size_mb: Optional[int] = 0
    total_new_asset_size_mb: Optional[int] = 0
    total_derivative_size_mb: Optional[int] = 0

    model_config = ConfigDict(extra='forbid')
