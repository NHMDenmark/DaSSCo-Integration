## Hpc_asset_creator script

**Where:**  
Runs on integration server.

**Inputs/conditions:**  
Requires that we can set up an SSH connection with an HPC server.  
Checks for assets in the track database where:  
- `hpc_ready` status: No  
- `jobs_status`: WAITING  
- `has_open_share`: YES  
- `is_in_ars`: YES  
- `has_new_file`: NO  
- `erda_sync`: YES  

**Description:**  
This script runs continually, checking if its conditions are met.  
It sets up an SSH connection with the HPC server that it keeps open.  
It looks through the track database for assets that meet the above conditions.  
Once such an asset has been found, it contacts the HPC server through the SSH connection and calls a script there with information found inside the track database for that asset. It also updates the status of the asset to reflect that the HPC has taken over.

**Outputs/Updates:**  
Updates the asset in the track database:  
- `hpc_ready`: WAITING  
Sends the following info in the call:  
- Path to the asset loader script on HPC  
- Asset GUID  
- HTTP link to the image in the file share  
- Batch ID  

**Calls:**  
HPC server's asset loader script[ https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_asset_loader.md].
