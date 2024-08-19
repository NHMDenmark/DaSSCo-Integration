## "asset_type"

**Type of field:**  
String  

**Part of which document:**  
Track

**Description:**  
Notes the type of asset we are dealing with. Uses the asset type enum list. Values can be: UNKNOWN, DEVICE_TARGET, LABEL and SPECIMEN. Unknown is used before the barcode is read and the asset subject has been found from the datamatrix.    

**Why do we have this field:**  
The field helps us know if special changes needs to be made to the jobs for the asset. Fex when an asset is discovered to be a device target we dont want to process this asset any further.  

**Populated by whom and when:**  
Integration server. When the asset is received.

**Updated where and when:**  
Integration server. When the barcode is read and the asset_subject field gets updated.