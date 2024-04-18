## "label_connections"

**Type of field:**  
List of strings

**Part of which document:**  
MOS

**Description:**  
List of guids belonging to assets connected through the same unique label id. 

**Why do we have this field:**  
Lets us know which assets are part of the same MOS.  

**Populated by whom and when:**  
Integration server when it receives an update denoting an asset as part of a MOS. 

**Updated where and when:**  
Integration server. Whenever another asset with the same unique_label_id is found. 

