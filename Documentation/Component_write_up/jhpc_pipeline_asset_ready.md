## HPC_pipeline asset_ready

**Where:**  
Runs on the HPC cluster.

**Inputs/conditions:**  
Receives one argument on invocation:
- asset_guid


**Description:**  
This component reptorts whether an asset has been loaded successfully into SLURM's local file system.

**Outputs/Updates:**  
Sends the following info in the call to [HPC_api_asset_ready](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_asset_ready.md):
- Asset_guid

**Calls:**  
Calls [HPC_api_asset_ready](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_asset_ready.md).
