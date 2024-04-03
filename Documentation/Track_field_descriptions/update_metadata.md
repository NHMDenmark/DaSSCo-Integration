## "update_metadata"

**Type of field:**  
String from the validate enum 

**Part of which document:**  
Track

**Description:**  
Uses the validate enum to show if an asset needs to have its metadata updated via the storage api. 

**Why do we have this field:**  
Lets us keep track of whether the metadata has been updated through ARS yet.   

**Populated by whom and when:**  
Integration server. When asset is received.   

**Updated where and when:**  
Integration server. When the metadata receives an update or the metadata has been updated through the storage api. 
