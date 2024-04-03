## "unique_label_id"

**Type of field:**  
String  

**Part of which document:**  
MOS

**Description:**  
Needed because labels are not necessarily unique. Assumes labels used on 1 day for a workstation are not reused. Consist of workstation name + date asset taken + label id. Which is the same as batch id + label id.  

**Why do we have this field:**  
Let clump together assets that are part of the same MOS.  

**Populated by whom and when:**  
Integration server when it receives an update denoting an asset as part of a MOS.  

**Updated where and when:**  
Never

