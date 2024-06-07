## HPC_pipeline assetUploader

**Where:**  
Runs on the HPC cluster.

**Inputs/conditions:**  
Receives three arguments on invocation:
- asset_guid

**Description:**  
This component derives an upload address to ARS from the asset GUID and uploads the file to this url.

**Outputs/Updates:**  
Sends the following info in the call to [Hpc_api endpoint derivative_uploaded]():
- Asset_guid

**Calls:**  
Calls [Hpc_api endpoint derivative_uploaded]().
