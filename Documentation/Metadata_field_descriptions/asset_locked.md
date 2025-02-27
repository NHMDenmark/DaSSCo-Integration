## "asset_locked"

**Type of field:**  
Boolean  

**Part of which document:**  
Metadata  

**Description:**  
Flags if it is possible to edit / delete the media of this asset. Note that this should only lock the media asset, not its associated metadata.

**Value:**  
True, False

**Why do we have this field:**  
Because it tells us something important  

**Populated by whom and when:**  
Set to false when asset is created by ARS.  

**Updated where and when:**  
Updated in ARS. When has not been decided.  

**Maps to in ARS:**  
asset_locked

**Maps to in Specify:**  
None

**Issues:**  
This does not exist in our metadata anymore. It should be deleted at some point from here. It is currently not possible to edit or add to an asset that has been locked in ARS. We are missing some option to do this. There is some not so important timing issues with it where you can add files to a share that was open before the assets metadata got updated to locked. 

