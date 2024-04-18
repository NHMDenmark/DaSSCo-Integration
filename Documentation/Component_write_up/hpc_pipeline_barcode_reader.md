## HPC_pipeline barcodeReader

**Where:**  
Runs on the HPC cluster.

**Inputs/conditions:**  
Receives one argument on invocation:
- asset_guid

**Description:**  
This component reads all barcodes in an asset. It subsequently separates all barcodes from the asset into specimen, disposable, or label barcodes. It checks whether the asset is a MSO (Multi specimen object) or part of a MOS (Multi object specimen). It assigns the asset_subject either label or specimen. It sends feedback to the integration server about when the asset has been barcode read successfully.

**Outputs/Updates:**  
Sends the following info in the call to [hpc_api_barcode](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_barcode.md) endpoint:
- asset_guid
- Job_name: barcodeReader
- Job_status: Done
- List of barcodes
- asset_subject
- Is MSO
- Is MOS
- Is label
- disposable_barcode

**Calls:**  
Calls [hpc_api_barcode](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_barcode.md).
