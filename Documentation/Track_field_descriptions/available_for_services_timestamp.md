## "available_for_services_timestamp"

**Type of field:**  
Datetime  

**Part of which document:**  
Track

**Description:**  
Timestamp telling when an asset had its "available_for_services" status changed from YES to PAUSED.

**Why do we have this field:**  
Allows for automatic checking of an asset and its status after a set amount of time has passed.

**Populated by whom and when:**  
Integration server when an asset changes from available to paused.  

**Updated where and when:**  
Integration server when an asset has its "available_for_services" status changed.