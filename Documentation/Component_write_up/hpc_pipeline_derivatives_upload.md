## HPC_pipeline derivatives upload

**Where:**  
Runs on the HPC cluster.

**Inputs/conditions:**  
Receives one argument on invocation:
- asset_guid

**Description:**  
This component uploads the derivative image identified by the asset_guid to the ARS openend share.
It reports to the [Hpc_api update_asset] endpoint that the job has finished.

**Outputs/Updates:**  
Sends the following info in the first call to [ARS upload endpoint]():
- image data

Sends the following info in the second call to [Hpc_api update_asset](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_update_asset.md) endpoint:
- asset_guid
- Job_name: derivative_upload
- Job_status: Done
- "data": { }

**Calls:**  
Calls [ARS upload endpoint], followed by [Hpc_api update_asset](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_update_asset.md).
