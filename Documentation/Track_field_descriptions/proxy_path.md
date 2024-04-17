## "proxy_path"

**Type of field:**  
String  

**Part of which document:**  
Track data  

**Description:**  
Path to the current open file proxy share. 

**Why do we have this field:**  
We need it to let other services know where to upload files belonging to the asset.  

**Populated by whom and when:**  
Integration server. Starts out empty when the asset is created.  

**Updated where and when:**  
When a share is opened/closed/synced the integration server updates the field.  