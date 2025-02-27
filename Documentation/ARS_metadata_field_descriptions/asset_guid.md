## "asset_guid"

**Type of field:**  
String  

**Part of which document:**  
ARS

**Description:**  
This is the unique GUID generated for each asset and is generated before incorporation into the storage system. Parts of the string are defined based on things such as the workstation and institution, the other parts are randomly generated. This is to enable a unique name for each asset. It is mandatory for our funding that we also have persistent identifiers for each asset (ideally resolvable as well). So we imagined an easy way to do this would be to incorporate the guid into a persistent identifier that can be clicked on to resolve (see asset_pid).

**Value:**  
Example: 7e8-7-17-14-1d-32-0-001-04-000-097367-00000

**Why do we have this field:**  
Allows us to uniquely identify each asset.

**Populated by whom and when:**  
Running IngestionClient/pipeline

**Updated where and when:**  
Never

