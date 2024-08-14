### Protocol: Event

An event is something that has changed an Asset or its metadata. 

| Fieldname Asset service | Desription | Datatype | Nullable | Notes |
|--|--|--|--|--| 
| pipeline | Name of the pipeline that started the event | String |  |  |
| workstation | Name of the workstation that was used | String |  |  |
| user | Username of the user that initiated the event | String |  |  |  
| event | What happened to the asset. | String enumeration CREATE_ASSET, UPDATE_ASSET, AUDIT_ASSET, DELETE_ASSET | no | 2023-09-08 T: Looks like we need to add the event types METADATA_CREATED and METADATA_UPDATED. Problem is that update and create asset are currently used for those. |
| (internal) asset_guid | The asset is connected to an event. |  | no | 2023-09-08 T: The events can be fetched from the webservice using the guid. The guid is currently not included in the returned json. |