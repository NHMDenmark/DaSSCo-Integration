## HPC_pipeline barcodeReader

**Where:**  
Runs on the HPC cluster.

**Inputs/conditions:**  
Receives one argument on invocation:
- asset_guid

**Description:**  
This component reads all text in the asset image. 

**Outputs/Updates:**  
Sends the following info in the call to [Hpc_api update_asset](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_update_asset.md) endpoint:
- asset_guid
- Job_name: OCR
- Job_status: Done
- "data": { "tags": {"ocr":oct_text}}

**Calls:**  
Calls [Hpc_api update_asset](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_update_asset.md).
