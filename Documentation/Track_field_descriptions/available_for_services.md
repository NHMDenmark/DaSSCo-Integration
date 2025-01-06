## "available_for_services"

**Type of field:**  
String  

**Part of which document:**  
Track

**Description:**  
Flag from the validation enum list. Used for letting micro services running on the integration server know if the asset is available. When set to PAUSED the asset_paused_status_handler service will keep track of the asset and return it to available once a set amount of time has passed.

**Why do we have this field:**  
Allowing integration server to pause an asset while something is being handled or waiting for a third party service fex.

**Populated by whom and when:**  
Integration server upon creation. 

**Updated where and when:**  
Integration server, when an asset should be made/not made available for the services.