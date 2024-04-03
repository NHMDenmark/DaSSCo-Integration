## "erda_sync"

**Type of field:**  
String  

**Part of which document:**  
Track

**Description:**  
This can be part of the file object populating the file_list or it can be the field for the entire document. The part for the file object tells if the specific file has been synced with Erda at some point. The general field shows what the overall status for the sync is- if there are any files that has not been synced the status will be negative and if every file has been synced it will be a positive.  

**Why do we have this field:**  
To keep track of whether files belonging to an asset has been synced with Erda.  

**Populated by whom and when:**  
Integration server. When an asset is received and for each file also whenever a new file is added to the asset.  

**Updated where and when:**  
Whenever an asset is synced with Erda or when a new file is received. 
