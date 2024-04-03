## "has_new_file"

**Type of field:**  
String, from the validate enum  

**Part of which document:**  
Track

**Description:**  
Tells if an asset has new files that have not yet been uploaded to ARS or added to the file_list.   

**Why do we have this field:**  
To keep track of when an asset has files that have not been persisted yet.   

**Populated by whom and when:**  
Integration server when the asset is received.  

**Updated where and when:**  
Whenever a new file is received or a file has been uploaded to ARS.
