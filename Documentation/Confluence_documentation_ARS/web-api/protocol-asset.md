## Protocol: Asset

Fields marked in red are either missing from the current protocol or potentially has errors.

Fields marked in yellow has inconsistant naming or is availble in a different format. 

Values are not generated unless specified in the Required column.

| Fieldname Asset service | Fieldname Spreadsheet | Desription | Datatype | Required in metadata | Action | Notes |
|--|--|--|--|--|--|--| 
| event.pipeline | asset_created_by | Pipeline, Workstation, Username | String | no - System generated when syncing ERDA. | Add | populated by DaSSCo storage upon receiving |
| event.pipeline | asset_deleted_by | An asset could be deleted by a pipeline (and therefore the name of the pipeline that deleted the asset will be shown here. This is taken from pipeline_name). An asset could also be deleted by a member of the project team if they have sufficient privileges. Mostly this will be very rare after the asset has been locked. A record of the file should remain even if the asset no longer exists if deleted following locking of the asset (post processing). | String | no - System generated on delete asset. | Add | populated by DaSSCo storage upon receiving |
| asset_guid | asset_guid | This is the unique GUID generated for each asset and is generated before incorporation into the storage system. Parts of the string are defined based on things such as the workstation and institution, the other parts are randomly generated. This is to enable a unique name for each asset. It is mandatory for our funding that we also have persistent identifiers for each asset (ideally resolvable as well). So we imagined an easy way to do this would be to incorporate the guid into a persistent identifier that can be clicked on to resolve (see asset_pid). | String | yes | rename DaSSCo storage | T: Deleted by assete/pipeline is available on AssetEvent |
| asset_locked | asset_locked | Flags if it is possible to edit / delete the media of this asset. Following the end of the processing associated with the pipeline and sync with Specify, assets (but not their metadata) should be locked. | boolean - defaults to false | no | |  B: can we lock the asset without its meta data ? T: Meta data can always be updated |
| asset_pid | asset_pid | See answer for asset_guid. One possible PID is to construct a URL like pid.dassco.dk/GUID1234555677243. This is then the unique and resolvable identifier that we will use when sharing. | String | no | rename DaSSCo storage |
| asset_subject | asset_subject | This is to define what the asset is a representation of | String | no |  | | 
| date_asset_taken | date_asset_taken | A date and time of when the original raw image was taken | ISO 8601:YYYY-MM-DDThh:mm:ssZ | no |  | 
| V2 feature audited | audited  | This is to mark the record as to having been manually audited. This will occur after complete processing and syncing with Specify. | boolean | no |  | | 
| V2 feature event.user? See: Protocol: Event | audited_by | This is the name of the person who audited the asset. Auditing will be done independently of the digitisation and usually by the technical team leader or a senior digitiser. | String | (yes) - a user must be provided when auditing |  | | 
| V2 feature event.timestamp? See: Protocol: Event | audited_date | This is the date the asset was audited. Auditing happens following complete processing of the asset following digitisation. | ISO 8601:YYYY-MM-DDThh:mm:ssZ | no - generated value |  | 
| specimens | - | A list of specimen opbjects with the following info: preparation_type, barcode and specimen_pid. | List of Specimen. | no - can be empty | |  2023-10-27 T:  A list of Specimens. See protocol: Specimen. This replaces the list of specimen_barcoes |
| collection | collection | This is the collection name (a collection of related specimens) within the institution that holds the specimen and should align with Specify collections for synchronisation (also part of specimen registration number for NHMA). | String | yes |  |  |
| date_asset_created | date_asset_created | When the file is uploaded and the samba share is closed; | ISO 8601:YYYY-MM-DDThh:mm:ssZ | no  Change command to receive timestamp | 2023-09-07 T: It seems that the dates from metadata and asset events are merged into one. What marks the creation of an asset, if not the date the metadata was uploaded? |
| date_asset_deleted | date_asset_deleted | ISO 8601:YYYY-MM-DDThh:mm:ssZ | no |  |  | 
| date_metadata_taken | date_metadata_created | Time metadata was originally created | ISO 8601:YYYY-MM-DDThh:mm:ssZ | no |  |  |
| event.pipeline See: Protocol: Event | date_metadata_uploaded | Time metadata was created in DaSSCo storage | ISO 8601:YYYY-MM-DDThh:mm:ssZ | no - generated value | B:not needed, but if already there then fine |  |
| event.pipeline See: Protocol: Event | date_metadata_updated | Set when the metadata is updated | ISO 8601:YYYY-MM-DDThh:mm:ssZ | no - generated value |  |  |
| digitiser | digitiser | This is the name of the person who imaged the specimens (creating the assets). This will be included in the metadata collected at the end of the days imaging during mass digitisation. It is the digitisers who also specify the pipeline at the end of the days digitisation, the pipeline will be run automatically. (Is date_asset_taken_by) | String | no | B:should it be renamed?? | 2023-09-07 T: It is assumed that this is some unique username. |
| V2 feature external_publisher | external_publisher | A list of URLs to external publisher sites or just names of the publishers, to which we are publishing this asset and a user can download the asset from the publisher (a reverse link). This should be searchable to see what is being published where. | PublicationLink | no - cannot be provided on initial metadata upload. | B: List |  | 
| file_format | file_format | The format of the asset | String Enumeration: TIF, JPEG, RAW, RAF, CR3, DNG, TXT | no | Extend list B: ideally end point ot to extend the list | 2023-09-07 T: Are we limited to those values? |
| funding | funding | A short description of funding source used to create the asset | String | no |  |  |
| institution | institution | The name of the Institution which owns and digitised the specimen | String | yes |  |  |
| event.pipeline See: Protocol: Event  | metadata_uploaded_by | Metadata could be created via a DaSSCo refinery pipeline, a scripted event (still a pipeline?) or via Specify | String | no - generated value | B: what does this field used for, is it some kind of history, event logging ?? | 2023-09-07 T: The value provided in the pipeline field |
| event.pipeline See: Protocol: Event | metadata_updated_by | Metadata can be updated manually, via pipelines and via Specify | String | no - generated value |  | 2023-09-07 T: The value provided in the pipeline field |
| multispecimen | multispecimen | Basically a multispecimen is a single image (or other type of media) that actually contains multiple specimens in it. Thus one asset is linked to multiple specimens. On one hand it is data that needs to carried through to Specify (multispecimen objects are modelled using containers in Specify); however, we can imagine needing to search on this in the storage registry to check the pipeline has worked as it should for these specimens and assets. But also, how many multispecimen objects we have dealt with is an important statistic for measuring and helping refine workflows. | boolean | no - generated value. true if more than one specimen barcode is provided. |  |  |
| parent_guid | parent_guid | This is the name of the parent media and in most cases will be the same as the original_parent_name, but can be different if a derivative of a derivative. | String | no | B: the field original_parent_name is deprecated |  |
| payload_type | payload_type | What the asset represents (important for how it is processed and when linking to Specify) | String | no |  |  |
| date_asset_finalised |  | Who syncs with specify? Asset Service or Pipeline? | ISO 8601:YYYY-MM-DDThh:mm:ssZ | no | B: rename to asset_finalised_date |  |
| restricted_access | restricted_access | We need to figure out how this would work when interacting with Specify. A specific script may need to be written. | List of string enumeration:  USER, ADMIN, SERVICE_USER, DEVELOPER | no | B: is this role based? |  |
| status | status | The current status of an asset. Should we indicate if it is being prcoessed or there is a problem, in this field? If it is being prcoessed that asset_locked field would be false, but I guess there may be other times that is so? What about if there is an issue. We need a way to see a quick summary in the UI of all issues. Not sure if this field would work for that? | String enumeration: WORKING_COPY, ARCHIVE, BEING_PROCESSED, PROCESSING_HALTED, ISSUE_WITH_MEDIA, ISSUE_WITH_METADATA, FOR_DELETION | yes | B: Possibility to extend list via end point |  |
| tags | tags | We are still developing our pipelines and can imagine the need to add additional fields in the future. It would be good to have a field to cover ourselves if we discover the need to additionally annotate our metadata assets until we can add more. | Map<String, String> | no |  |  |
| workstation_name | workstation_name | This is the name of the workstation used to do the imaging. The name of the work_station, was used when working on this create, update or delete request. | The name of the workstation | yes |  |  |
| update_user | NTECH_G90311 | Username of the person that updated the asset | String | yes |  |  |
| pipeline_name | pipeline_name | The name of the Pipeline, which has sent an create, update or delete request to the storage service. It is the pipeline that creates the asset, but we will create derivatives (multiple assets per specimen), so will probably need to explore this in relation to specimen as well. Need to check if mandatory to create an asset (e.g., when adding assets other than via a mass digitisation pipeline). | String | yes |  |  |
| internal_status |  | METADATA_RECEIVED: The metadata has been received and a share where files can be uploaded has been created. ASSET_RECEIVED: Assets that are pending ERDA synchronisation has this status. COMPLETED: Assets has been successfully synchronised with ERDA. It is still possible to open shares for assets with this status and update them as long as asset_locked status is not true. ERDA_ERROR: Synchronisation failed. ERDA sync has encountered some errors and have exhausted the retry attempts. | String enumeration: METADATA_RECEIVED, ASSET_RECEIVED, COMPLETED, ERDA_ERROR |  |  |  |

## Protocol: Specimen
Specimens are created together with assets and they inherit the institution and collection from the asset it was created with. It another asset is created with a specimen containing the same information it will be linked to the previously created specimen.

| Fieldname Asset service | Fieldname Spreadsheet | Desription | Datatype | Required in specimen | Action | Notes |
|--|--|--|--|--|--|--| 
| barcode | barcode | This refers to a physical barcode on the specimen consisting of 8 digits. It is part of an ID unique to that specimen and consisting of: An institution acronym, a collection acronym, and the barcode. We can have one specimen barcode related to multiple assets and in sme cases one asset with multiple specimen barcodes (an example of the later is a multispecimen herbarium sheet). | String | yes | rename in NHMD metadata, B: not bound to 8 or 9, - no validation in dassco storage, associated with institution and collection to unique resolve specimens |  |
| preparation_type | preparation_type | This relates to the way the specimen has been prepared (e.g., a pinned insect or mounted on a slide). Whilst this is specimen data, it is also fundamental to how we are keeping track of the project - as the different ways a specimen is prepared will affect our planning, our pipelines, reporting etc. Hence, incorporating this field into the registry makes sense. | String | no |  |  |
| specimen_pid | specimen_pid | We need a system to uniquely resolve assets. We don't currently have a system in place for this. We need to develop this. | String |  | To be discussed |  |
| institution | asset.institution |  | String | no - taken from the asset metada |  |  |
| collection |  |  | String | no - taken from the asset metada |  |  | 

### Internal_status
|  |  |
|--|--|
| METADATA_RECEIVED, ASSET_RECEIVED, COMPLETED, ERDA_ERROR | |

 

 

 