## Hpc_api endpoint asset_ready

**Where:**  
Runs on the integration server.

**Inputs/conditions:**  
Receives the `asset_guid`.

**Description:**  
Receives the call when the asset has been created on the HPC server. Checks that the asset exists and updates the track database for the asset.

**Outputs/Updates:**  
Updates track database:  
- `hpc_ready`: YES  
Returns an HTTP status code of 200 if everything updated correctly and 422 if things went wrong.

**Calls:**  
None
