## Hpc_api barcode endpoint

**Where:**  
Runs on the integration server.

**Inputs/conditions:**  
Receives a barcode model:
- asset_guid
- job_name
- job_status
- List of barcodes
- asset_subject
- Is MSO
- Is MOS
- Is label
- disposable_barcode

**Description:**  
Receives a barcode model when the endpoint is called. Checks that the barcode model is correctly filled out and that the asset exists. If this fails, returns a failed status. Updates the metadata file in the local database and updates the track file in the database. Checks if the asset is an MOS. If an asset is an MOS, it creates the data needed to create a new entry in the MOS database using the disposable ID and the batch ID of the asset. Then updates assets connected to it through the unique label ID in the MOS database. Checks if the asset is a label and updates its metadata file in the database with the barcodes of connected assets. If the asset is not a label, checks if there is a label connected to it and if so, updates the label with the barcode of the asset.

**Outputs/Updates:**  
Update in metadata database:  
- barcodes
- multispecimen
- Asset_subject

Update in track database:  
- job_status

If asset is MOS, create in MOS database:  
MOS model:
- Is label
- spid
- disposable_id
- unique_label_id
- List of connected assets GUIDs

Update connected label asset in metadata database:  
- barcode

If asset is label, create in MOS database:  
MOS model:
- Is label
- spid
- disposable_id
- unique_label_id
- List of connected assets GUIDs

Update asset in metadata database:  
- barcode (with barcodes from connected assets)

Returns an HTTP status code of 200 if everything updated correctly and 422 if things went wrong.

**Calls:**  
None.
