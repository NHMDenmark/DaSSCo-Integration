## "has_open_share"

**Type of field:**  
String, from the validate enum 

**Part of which document:**  
Track

**Description:**  
Shows whether an asset currently has an open file share.  

**Why do we have this field:**  
It is very important that we do not open multiple file shares for an asset. This will crash the file share and the asset files/ and the file share will be unable to be accessed, updated or synced.  

**Populated by whom and when:**  
Integration server. When the asset is received.  

**Updated where and when:**  
Intgration server. Whenever the assets fileshare is created, opened, deleted or the asset is synced with Erda. 
