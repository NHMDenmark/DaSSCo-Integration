## "asset_created_by"

**Type of field:**  
String  

**Part of which document:**  
Metadata  

**Description:**  
An asset is created by a pipeline or sync with Specify. Hence this field will be the name of the pipeline that created the asset. It could also be created via a specific intervention - e.g., transferring assets from one place to another. Would it therefore be the person scripting this or logged on that appears as a name here?  

**Value:**  
None  

**Why do we have this field:**  
It tells where the asset originated from.   

**Populated by whom and when:**  
Upon event  

**Updated where and when:**  
Never  

**Maps to in ARS:**  
None

**Maps to in Specify:**  
None

**Issues:**  
This could be part of the event protocol in ARS populating the user field. Currently that field will be populated by the digitiser when you create a new asset in ARS. The field does not exist as such in ARS. NT documentation says this should be filled when asset is synced with erda. 

