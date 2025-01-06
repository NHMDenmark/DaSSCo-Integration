## "available_for_services_wait_time"

**Type of field:**  
Integer  

**Part of which document:**  
Track

**Description:**  
Set amount of time in seconds an asset will be paused.

**Why do we have this field:**  
Allows configuring the amount of time necessary for other things to happen before unpausing. 

**Populated by whom and when:**  
Integration server service when asset is paused.  

**Updated where and when:**  
Reset when unpaused.