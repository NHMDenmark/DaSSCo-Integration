## "metadata_origin"

**Type of field:**  
String, from the metadata_origin enum

**Part of which document:**  
Track

**Description:**  
Displays the origin of the metadata relative to the integration server. Allows tracking of where/how the integration server received the metadata. 

**Why do we have this field:**  
Its needed for knowing which overall flow is required for the asset while being processed in its pipeline. 

**Populated by whom and when:**  
Integration server. When an assets metadata is received and handled.

**Updated where and when:**  
Never