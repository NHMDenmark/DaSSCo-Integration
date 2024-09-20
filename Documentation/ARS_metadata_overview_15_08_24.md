| Name | Type of field | Part of which document | Description | Value | Why do we have this field | Populated by whom and when | Updated where and when |
| --- | --- | --- | --- | --- | --- | --- | --- |
| allocated_storage_mb | Integer | ARS | The amount of storage allocated on the server to the new asset | A number in megabytes (mb). | Because it tells us something important | ARS. Populated as part of the httpInfo protocol | When the assets fileshare changes |
| allocation_status_text | String | ARS | A detailed error message if an error happens | SUCCESS  : A share was successfully created or allocation was successfully changed. DISK_FULL : There is not enough disk space for the requested allocation. BAD_REQUEST : Changing the storage allocation to a lower amount than than is already used. UPSTREAM_ERROR : An issue with an external system happened. It could be a failure to download the parent asset from ERDA or a call to asset service from the file-proxy that fails. SHARE_NOT_FOUND : The share you are trying to update doesnt exist. INTERNAL_ERROR : Some unexpected internal error happened. | Gives us information about the status of the call made to ARS. | ARS. Populated as part of the httpInfo protocol | When the assets fileshare changes |
| asset_guid | String | ARS | This is the unique GUID generated for each asset and is generated before incorporation into the storage system. Parts of the string are defined based on things such as the workstation and institution, the other parts are randomly generated. This is to enable a unique name for each asset. It is mandatory for our funding that we also have persistent identifiers for each asset (ideally resolvable as well). So we imagined an easy way to do this would be to incorporate the guid into a persistent identifier that can be clicked on to resolve (see asset_pid). | Example: 7e8-7-17-14-1d-32-0-001-04-000-097367-00000 | Allows us to uniquely identify each asset. | Running IngestionClient/pipeline | Never |
| asset_locked | Boolean | ARS | Should flag if it is possible to edit / delete the media of this asset. Note that this should only lock the media asset, not its associated metadata. | True or False | Because it tells us something important | Set to false when asset is created by ARS. | Updated in ARS. When has not been decided. |
| asset_pid | String | ARS | Missing description | TBD | TBD | TBD | TBD |
| audited | Boolean | ARS | This is to mark the record as to having been manually audited. This will occur after complete processing and syncing with Specify. | True or False | - | Ingestion client | Integration server. After sync with specify and processing has finished |
| barcode | String | ARS | Barcode belonging to a specimen. This belongs to the specimens protocol and is part of the specimens object. | 9 or 10 digits as a string | Lets us identify the specimen and link it with Specify. | ARS. Populated as part of the specimen protocol when a barcode is given to ARS by either specify or integration server | Never |
| cache_storage_mb | Integer | ARS | The total amount of storage dedicated for �caching� files for external linking and other use. | A number in megabytes (mb). | Because it tells us something important | ARS. Populated as part of the httpInfo protocol | When the assets fileshare changes |
| collection | String | ARS | The collection the asset came from | Vascular-plants | Because it tells us something important | Ingestion server. When the metadata is created. | Never |
| collection_specimen | String | ARS | The collection the specimen belongs to. This belongs to the specimens protocol and is part of the specimens object. | Vascular-plants | Because it tells us something important | ARS. Populated as part of the specimen protocol when a barcode is given to ARS by either specify or integration server | Never |
| created_date | Datetime | ARS | Timestamp for when the asset was created in ARS | ISO 8601:YYYY-MM-DDThh:mm:ssZ or NULL | Because it tells us something important | ARS. When the assets metadata is received in ARS. | Never |
| date_asset_deleted | Datetime | ARS | Timestamp for when the asset was deleted | ISO 8601:YYYY-MM-DDThh:mm:ssZ or NULL | Because it tells us something important | TBD | Never |
| date_asset_finalised | Datetime | ARS | Timestamp for when the asset was finalised | ISO 8601:YYYY-MM-DDThh:mm:ssZ or NULL | Because it tells us something important | TBD | Never |
| date_asset_taken | Datetime | ARS | Timestamp for when the asset was taken | ISO 8601:YYYY-MM-DDThh:mm:ssZ or NULL | Because it tells us something important | Originates from the workstation and is populated by the ingestion server | Never |
| date_metadata_taken | Datetime | ARS | Time metadata was originally created | ISO 8601:YYYY-MM-DDThh:mm:ssZ or NULL | Because it tells us something important | Ingestion server when metadata is created | Never |
| date_metadata_updated | Datetime | ARS | Timestamp for when the metadata was updated | ISO 8601:YYYY-MM-DDThh:mm:ssZ or NULL | Because it tells us something important | ARS whenever the metadata is updated. | When a new update is made |
| digitiser | String | ARS | This is the name of the person who imaged the specimens (creating the assets). This will be included in the metadata collected at the end of the days imaging during mass digitisation. It is the digitisers who also specify the pipeline at the end of the days digitisation, the pipeline will be run automatically. This won't be filled in when image is added direct from Specify. Instead, in that case, the author would be filled in in the attachments metadata in Specify. | Amanda Louisa Elizabeth Cory Marcussen | Because it tells us something important | Ingestion server | Never |
| error_message | String | ARS | The error we received while working with the asset, for example: �Connection Reset, while uploading to ERDA�, only sent if �an error occurred | None | Because it tells us something important | ARS when an event of any kind that results in a predetermined error occurs. | Never |
| error_timestamp | Datetime | ARS | If an error occured when did it happen | ISO 8601:YYYY-MM-DDThh:mm:ssZ or NULL | Because it tells us something important | ARS when an error occurs | Never |
| event | String | ARS | What happened to the asset. | String enumeration CREATE_ASSET, UPDATE_ASSET, AUDIT_ASSET, DELETE_ASSET | Because it tells us something important | ARS. Populated as part of the event protocol. | When a new event is registered in ARS |
| events | String | ARS | List of the events that has occurred with the asset. | Event objects contains: user, event_pipeline, event_workstation and timestamp | Because it tells us something important | ARS. Populated as part of the event protocol. | When a new event is registered in ARS |
| event_name | String | ARS | Missing description | None | We do not what this is, so far it has never filled out. | ARS. Populated as part of the event protocol. | When a new event is registered in ARS |
| event_pipeline | String | ARS | Name of the pipeline that started the event | None | Because it tells us something important | ARS. Populated as part of the event protocol. | When a new event is registered in ARS |
| event_workstation | String | ARS | Name of the workstation that was used | None | Because it tells us something important | ARS. Populated as part of the event protocol. | When a new event is registered in ARS |
| file_formats | List of enums | ARS | List of file formats the files belonging to an asset has. | TIF, JPEG etc | Because it tells us something important | Ingestion server. When the metadata is created. | Never |
| funding | String | ARS | Who funded the digitisation of the asset. | DaSSCo | Because it tells us something important | Ingestion server. When the metadata is created. | Never |
| hostname | String | ARS | Where the asset files can be posted to. The hostname can be combined with the asset path to form an url where asset files can be posted og downloaded. | None | Because it tells us something important | ARS. Populated as part of the httpInfo protocol | When the assets fileshare changes |
| httpInfo | Dictionary object | ARS | This is the object containing the information about file shares and the storage space used. | None | Protocol decision | ARS. Populated as part of the httpInfo protocol | When the assets fileshare changes |
| http_allocation_status | String | ARS | Status for using the a share. | String enumeration: �SUCCESS, DISK_FULL, ILLEGAL_STATE, UPSTREAM_ERROR, SHARE_NOT_FOUND, INTERNAL_ERROR | Because it tells us something important | ARS. Populated as part of the httpInfo protocol | When the assets fileshare changes |
| institution | String | ARS | The institution the asset belongs to. | NHMA | Because it tells us something important | Ingestion server. When the metadata is created. | Never |
| institution_specimen | String | ARS | The institution the specimen belongs to. This belongs to the specimens protocol and is part of the specimens object. | NHMD | Because it tells us something important | ARS. Populated as part of the specimen protocol when a barcode is given to ARS by either specify or integration server | Never |
| internal_status | String | ARS | The status that ARS keeps track of an asset with. | COMPLETED, ASSET_RECEIVED, ERDA_ERROR, METADATA_RECEIVED | The integration server uses this to keep track of it an asset has synced with erda. | ARS, when asset is created in ARS. | ARS when asset changes status. |
| multi_specimen | Boolean | ARS | Tells if the asset contains multiple specimens. | True or False | Because it tells us something important | Ingestion server. When the metadata is created. | Never |
| parent_guid | String  or null | ARS | If the asset is derived from a parent asset then this will be true. | Null or an asset guid | Because it tells us something important | When the assets metadata is created either by the ingestion server or a job run on hpc. | Never |
| path | String | ARS | The path to the asset. | None | Because it tells us something important | ARS. Populated as part of the httpInfo protocol | Never |
| payload_type | String | ARS | What the asset contain, could be images, ct-scans etc | image | Because it tells us something important | Ingestion server. When the metadata is created. | Never |
| pipeline | String | ARS | Which pipeline does the asset belong to | PIPEHERB8888 | Because it tells us something important | Ingestion server. When the metadata is created. | Never |
| preparation_type | String | ARS | This relates to the way the specimen has been prepared (e.g., a pinned insect or mounted on a slide). This belongs to the specimens protocol and is part of the specimens object. | Examples: sheet, pinned, dry | Because it tells us something important | ARS. Populated as part of the specimen protocol when a barcode is given to ARS by either specify or integration server | Never |
| remaining_storage_mb | Integer | ARS | The remaining storage on the server: total - cache - all_allocated = remaining | A number in megabytes (mb). | Because it tells us something important | ARS. Populated as part of the httpInfo protocol | When the assets fileshare changes |
| restricted_access | String | ARS | List of users with access in some capacity. The specifics have not been decided yet. | ADMIN, USER this havent been fully decided | Because it tells us something important | Note | Never |
| specimens | String | ARS | This is a list of specimens objects that belong to an asset. It belongs to the specimen protocol. | A specimens object contains: institution_specimen, collection_specimen, barcode, specimen_pid and preparation_type. | Protocol decision | ARS. Populated as part of the specimen protocol when a barcode is given to ARS by either specify or integration server | Never |
| specimen_pid | String | ARS | Missing description. This belongs to the specimens protocol and is part of the specimens object. | None | Because it tells us something important | ARS. Populated as part of the specimen protocol when a barcode is given to ARS by either specify or integration server | Never |
| status | String | ARS | The status of the asset, comes from an enum list. | FOR_PROCESSING, BEING_PROCESSED, WORKING_COPY, ARCHIVE, PROCESSING_HALTED, FOR_DELETION, ISSUE_WITH_MEDIA, ISSUE_WITH_METADATA | It is not for the services use but for human eyes to quickly give an overview. | When the asset is created or received initially | When the asset changes status |
| subject | String | ARS | This is to define what the asset is a representation of | Example: folder | Because it tells us something important | Ingestion client when metadata is created | ARS/Integration server if asset has new media added |
| tags | Dictionary containing key strings each with a value string. | ARS | We are still developing our pipelines and can imagine the need to add additional fields in the future. It would be good to have a field to cover ourselves if we discover the need to additionally annotate our metadata assets until we can add more. | A dictionary of dynamic propertiesFx "ocr": ocr_tex | Gives us flexibility to incorporate new information or make changes without having to overhaul the whole system immediately. | Can be populated by anyone at anytime. | Anytime and anywhere. |
| timestamp | Datetime | ARS | The timestamp of the event happening. Example event could be update metadata in ARS. | ISO 8601:YYYY-MM-DDThh:mm:ssZ or NULL | Let us know when an event happened. | ARS. Populated as part of the event protocol. | When a new event is registered in ARS |
| total_storage_mb | Integer | ARS | The total storage of the server where the FileProxy is deployed. | A number in megabytes (mb). | Because it tells us something important | ARS. Populated as part of the httpInfo protocol | When the assets fileshare changes |
| update_user | String | ARS | The user doing the operation. | Either a person or a service. | Because it tells us something important | The user updating the metadata. | Whenever an update is made |
| user | String | ARS | The user who did the operation. | Either a person or a service. | Because it tells us something important | ARS. Populated as part of the event protocol. When an event happens the user who started the event gets registered | When |
| workstation | String | ARS | The asset was created at this workstation. Parent workstation if the asset is derived. | WORKHERB9999 | Because it tells us something important | Ingestion server. When the metadata is created. | Never |
| writeAccess | Boolean | ARS | Missing description | True or False | Because it tells us something important | Note | Never |