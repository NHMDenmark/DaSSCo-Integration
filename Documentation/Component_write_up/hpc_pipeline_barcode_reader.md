## HPC_pipeline barcodeReader

**Where:**  
Runs on the HPC cluster.

**Inputs/conditions:**  
Receives one argument on invocation:
- asset_guid

**Description:**  
This component reads all barcodes in an asset. It subsequently separates all barcodes from the asset into specimen, disposable, or label barcodes. It checks whether the asset is a MSO (Multi specimen object) or part of a MOS (Multi object specimen). It assigns the asset_subject either label or specimen. It sends feedback to the integration server about 

a) whether it could queue the barcodeReader into the execution queue and 
b) when the asset has been barcode read successfully.

**Outputs/Updates:**  
Sends the following info in the a) call to Hpc_api endpoint queue_job:
- Asset_guid
- Job_name: barcodeReader
- Job_id: HPC job ID if the queue is not already full, otherwise -1
- Timestamp

Sends the following info in the b) call to Hpc_api barcode endpoint:
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
Calls Hpc_api endpoint queue_job and, in case of success, Hpc_api barcode endpoint.
