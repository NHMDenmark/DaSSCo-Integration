## "hpc_ready"

**Type of field:**  
String, from the validate enum  

**Part of which document:**  
Track

**Description:**  
This tells whether an asset has had its files succesfully moved onto the hpc server.  

**Why do we have this field:**  
We need to know this before we start running processes on the asset on the hpc server.  

**Populated by whom and when:**  
Integration server. When an asset is received. 

**Updated where and when:**  
Integration server. When receiving information from the hpc server through the hpc api that the asset files have been moved to the hpc server. 
