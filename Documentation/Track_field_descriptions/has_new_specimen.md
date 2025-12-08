## "has_new_specimen"

**Type of field:**  
String, from the validate enum. 

**Part of which document:**  
Track

**Description:**  
Tells if an asset has new specimens (barcodes) that have not yet been created in ARS.  

**Why do we have this field:**  
Specimens has to be created before they can be added to the metadata in ARS. This lets us keep track of whether a specimen needs to be created. 

**Populated by whom and when:**  
Integration server when the asset is received.  

**Updated where and when:**  
Whenever barcodes are updated for an asset or a specimen has been created in ARS. 