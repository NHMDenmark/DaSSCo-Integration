## "asset_size"

**Type of field:**  
Integer  

**Part of which document:**  
Track

**Description:**  
Keeps track of the total size of an assets files. It is computed from the individual file sizes that belong to an asset.   

**Why do we have this field:**  
We need to know how much space to request when opening a file share for an asset.  

**Populated by whom and when:**  
Integration server. When the asset is received.

**Updated where and when:**  
Integration server. Whenever a new file is added to the asset or a file is deleted from the asset. 
