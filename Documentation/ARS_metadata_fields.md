| Meta Data Field name in json   | Written by          | When          | Saved where        | When       | Relevant into      |
|--------------------------------|---------------------|---------------|--------------------|------------|--------------------|
| [asset_pid](ARS_metadata_field_descriptions/asset_pid.md) | TBD | TBD | ARS/Integration | Upon ARS call | We have not determined what, how or when this field gets filled out. | 
| [asset_guid](ARS_metadata_field_descriptions/asset_guid.md) | Ingestion server | Upon event | ARS/Integration | When asset is received | |
| [status](ARS_metadata_field_descriptions/status.md) | Ingestion server | Upon creation | ARS/Integration | When asset is received | Status for human users of the pipeline. |
| [multi_specimen](ARS_metadata_field_descriptions/multi_specimen.md) | Integration server | Upon event | ARS/Integration | After asset is processed | |
| x | d | x | d | x | d |
| [specimens](ARS_metadata_field_descriptions/specimens.md) | ARS | Upon event | ARS | When barcode is added | This is a list of specimens belonging to an asset. It belongs to the specimen protocol. |
| [institution](ARS_metadata_field_descriptions/institution_specimen.md) | ARS | TBD | ARS | When barcode is added | This belongs to the specimens protocol and is part of the [specimens](ARS_metadata_field_descriptions/institution.md) object.. |
| [collection](ARS_metadata_field_descriptions/collection_specimen.md) | ARS | TBD | ARS | When barcode is added | This belongs to the specimens protocol and is part of the [specimens](ARS_metadata_field_descriptions/collection.md) object. |
| [barcode](ARS_metadata_field_descriptions/barcode.md) | ARS | Upon event | ARS | When barcode is added | This belongs to the specimens protocol and is part of the [specimens](ARS_metadata_field_descriptions/barcode.md) object.. |
| [specimen_pid](ARS_metadata_field_descriptions/specimen_pid.md) | ARS | TBD | ARS | When barcode is added | This belongs to the specimens protocol and is part of the [specimens](ARS_metadata_field_descriptions/specimen_pid.md) object. |
| [preparation_type](ARS_metadata_field_descriptions/preparation_type.md) | Upon event | Upon event | ARS | When barcode is added | This belongs to the specimens protocol and is part of the [specimens](ARS_metadata_field_descriptions/preparation_type.md) object. |
| x | d | x | d | x | d |
| [funding](ARS_metadata_field_descriptions/funding.md) | Ingestion Server | Upon creation | ARS/Integration | Upon event |  |
| [subject](ARS_metadata_field_descriptions/subject.md) | Ingestion Server | Upon creation | ARS/Integration | Upon event |  |
| [payload_type](ARS_metadata_field_descriptions/payload_type.md) | Ingestion Server | Upon creation | ARS/Integration | Upon event |  |
| [file_formats](ARS_metadata_field_descriptions/file_formats.md) | Ingestion Server | Upon creation | ARS/Integration | Upon event | List of file formats from an enum list. |
| [asset_locked](ARS_metadata_field_descriptions/asset_locked.md) | Ingestion Server | Upon creation | ARS/Integration | Upon event |  |
| [restricted_access](ARS_metadata_field_descriptions/restricted_access.md) | TBD | TBD | ARS/Integration | TBD |  |
| [tags](ARS_metadata_field_descriptions/tags.md) | Anyone | Anytime | ARS/Integration | Anytime | Catch all field that gives flexibility. |
| [audited](ARS_metadata_field_descriptions/audited.md) | TBD | TBD | ARS/Integration | TBD |  |
| [created_date](ARS_metadata_field_descriptions/created_date.md) | Ingestion Server | Upon creation | ARS/Integration | Upon event |  |
| [date_metadata_updated](ARS_metadata_field_descriptions/date_metadata_updated.md) | ARS | Upon event | ARS | Upon event | This is the last known update date. |
| [date_asset_taken](ARS_metadata_field_descriptions/date_asset_taken.md) | Ingestion Server | Upon creation | Integration/ARS | Upon event |  |
| [date_asset_deleted](ARS_metadata_field_descriptions/date_asset_deleted.md) | ARS | Upon event | ARS | Upon event |  |
| [date_asset_finalised](ARS_metadata_field_descriptions/date_asset_finalised.md) | ARS | Upon event | ARS | Upon event |  |
| [date_metadata_taken](ARS_metadata_field_descriptions/date_metadata_taken.md) | ARS | Upon event | ARS | Upon event |  |
| [institution](ARS_metadata_field_descriptions/institution.md) | Ingestion Server | Upon creation | Integration/ARS | Upon event |  |
| [collection](ARS_metadata_field_descriptions/collection.md) | Ingestion Server | Upon creation | Integration/ARS | Upon event |  |
| [parent_guid](ARS_metadata_field_descriptions/parent_guid.md) | Integration Server | Upon creation | Integration/ARS | Upon event |  |
| [internal_status](ARS_metadata_field_descriptions/internal_status.md) | ARS | Upon event | ARS | Upon event | This is an ARS only status |
| [update_user](ARS_metadata_field_descriptions/update_user.md) | Integration Server | Upon event | ARS | Upon event |  |
| x | d | x | d | x | d |
| [events](ARS_metadata_field_descriptions/events.md) | ARS | Upon event | ARS | Upon event | This is a list of events that occurered with the asset belonging to the event protocol. |
| [user](ARS_metadata_field_descriptions/user.md) | ARS | Upon event | ARS | Upon event | This belongs to the events protocol and is part of the [events](ARS_metadata_field_descriptions/events.md) object. |
| [timestamp](ARS_metadata_field_descriptions/timestamp.md) | ARS | Upon event | ARS | Upon event | This belongs to the events protocol and is part of the [events](ARS_metadata_field_descriptions/events.md) object. |
| [event](ARS_metadata_field_descriptions/event.md) | ARS | Upon event | ARS | Upon event | This belongs to the events protocol and is part of the [events](ARS_metadata_field_descriptions/events.md) object. |
| [pipeline](ARS_metadata_field_descriptions/event_pipeline.md) | ARS | Upon event | ARS | Upon event | This belongs to the events protocol and is part of the [events](ARS_metadata_field_descriptions/events.md) object. |
| [workstation](ARS_metadata_field_descriptions/event_workstation.md) | ARS | Upon event | ARS | Upon event | This belongs to the events protocol and is part of the [events](ARS_metadata_field_descriptions/events.md) object. |
| x | d | x | d | x | d |
| [digitiser](ARS_metadata_field_descriptions/digitiser.md) | Ingestion Server | Upon creation | Integration/ARS | Upon event |  |
| [workstation](ARS_metadata_field_descriptions/workstation.md) | Ingestion Server | Upon creation | Integration/ARS | Upon event |  |
| [pipeline](ARS_metadata_field_descriptions/pipeline.md) | Ingestion Server | Upon creation | Integration/ARS | Upon event |  |
| [error_message](ARS_metadata_field_descriptions/error_message.md) | ARS | Upon event | - | - | Figure out how this works. Not sure if it gets persisted in ARS? |
| [error_timestamp](ARS_metadata_field_descriptions/error_timestamp.md) | ARS | Upon event | - | - | Same as error_message |
| [event_name](ARS_metadata_field_descriptions/event_name.md) | ARS | Upon event | - | - | Same as error_message |
| [writeAccess](ARS_metadata_field_descriptions/writeAccess.md) | ARS | Upon event | ARS | Upon event | Not sure how this works either |
| x | d | x | d | x | d |
| [httpInfo](ARS_metadata_field_descriptions/httpInfo.md) | ARS | Upon creation | ARS | Upon event | This is a object containing the file share information for the created asset. |
| [path](ARS_metadata_field_descriptions/path.md) | ARS | Upon event | - | - | Part of the [httpInfo](ARS_metadata_field_descriptions/httpInfo.md) object received when we create an asset with ARS. |
| [hostname](ARS_metadata_field_descriptions/hostname.md) | ARS | Upon event | - | - | Part of the [httpInfo](ARS_metadata_field_descriptions/httpInfo.md) object received when we create an asset with ARS.
| [total_storage_mb](ARS_metadata_field_descriptions/total_storage_mb.md) | ARS | Upon event | - | - | Part of the [httpInfo](ARS_metadata_field_descriptions/httpInfo.md) object received when we create an asset with ARS.
| [cache_storage_mb](ARS_metadata_field_descriptions/cache_storage_mb.md) | ARS | Upon event | - | - | Part of the [httpInfo](ARS_metadata_field_descriptions/httpInfo.md) object received when we create an asset with ARS.
| [remaining_storage_mb](ARS_metadata_field_descriptions/remaining_storage_mb.md) | ARS | Upon event | - | - | Part of the [httpInfo](ARS_metadata_field_descriptions/httpInfo.md) object received when we create an asset with ARS.
| [allocated_storage_mb](ARS_metadata_field_descriptions/allocated_storage_mb.md) | ARS | Upon event | - | - | Part of the [httpInfo](ARS_metadata_field_descriptions/httpInfo.md) object received when we create an asset with ARS.
| [allocation_status_text](ARS_metadata_field_descriptions/allocation_status_text.md) | ARS | Upon event | - | - | Part of the [httpInfo](ARS_metadata_field_descriptions/httpInfo.md) object received when we create an asset with ARS.
| [http_allocation_status](ARS_metadata_field_descriptions/http_allocation_status.md) | ARS | Upon event | - | - | Part of the [httpInfo](ARS_metadata_field_descriptions/httpInfo.md) object received when we create an asset with ARS.
| x | d | x | d | x | d |