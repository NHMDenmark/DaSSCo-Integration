## "internal_status"

**Type of field:**  
String  

**Part of which document:**  
ARS

**Description:**  
The status that ARS keeps track of an asset with.

**Value:**  
COMPLETED, ASSET_RECEIVED, ERDA_ERROR, METADATA_RECEIVED

**Why do we have this field:**  
The integration server uses this to keep track of it an asset has synced with erda.

**Populated by whom and when:**  
ARS, when asset is created in ARS.

**Updated where and when:**  
ARS when asset changes status.

