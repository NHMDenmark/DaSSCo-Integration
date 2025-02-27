## "date_metadata_updated"

**Type of field:**  
String  

**Part of which document:**  
Metadata

**Description:**  
Timestamp for when an assets metadata was updated.   

**Value:**  
ISO 8601:YYYY-MM-DDThh:mm:ssZ or NULL

**Why do we have this field:**  
Lets us keep track of when an asset had its metadata updated.   

**Populated by whom and when:**  
Event based and populated by ARS

**Updated where and when:**  
After each update to an assets metadata in ARS 

**Maps to in ARS:**  
None

**Maps to in Specify:**  
None

**Issues:**  
We can only keep one value here despite the asset potentially having its metadata updated multiple times. 

