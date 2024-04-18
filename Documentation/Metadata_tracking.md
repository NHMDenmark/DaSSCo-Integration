| Meta Data Field name in json   | Written by          | When          | Saved where        | When       | Relevant into      |
|--------------------------------|---------------------|---------------|--------------------|------------|--------------------|
| [asset_created_by](Data_field_descriptions/asset_created_by.md) | ARS | Upon event | ARS | Upon ARS call | |
| [asset_deleted_by](Data_field_descriptions/asset_deleted_by.md) | ARS | Upon event | ARS | Upon ARS call | |
| [asset_guid](Data_field_descriptions/asset_guid.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration call / Upon ARS call |
| [asset_pid](Data_field_descriptions/asset_pid.md) | TBD | TBD | ARS / Integration | TBD | We have not figured out what this is or how its created yet. |
| [asset_subject](Data_field_descriptions/asset_subject.md) | Pipeline | Running pipeline | ARS / Integration | Upon ARS call / Upon Integration call | |
| [date_asset_taken](Data_field_descriptions/date_asset_taken.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call |
| [asset_updated_by](Data_field_descriptions/asset_updated_by.md) | TBD | TBD | TBD | TBD | Decision needs to be made on this field. Should it be a list and if so how should it map with date_asset_updated |
| [audited](Data_field_descriptions/audited.md) | TBD | | | | |
| [audited_by](Data_field_descriptions/audited_by.md) | TBD | | | | |
| [audited_date](Data_field_descriptions/audited_date.md) | TBD | | | | |
| [barcode](Data_field_descriptions/barcode.md) | Pipeline | Running pipeline | Integration / ARS | Upon integration call / Upon ARS call | |
| [collection](Data_field_descriptions/collection.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call |
| [date_asset_created](Data_field_descriptions/date_asset_created.md) | ARS | Upon event | ARS | Upon ARS call | Stamp for creation with ARS |
| [date_asset_deleted](Data_field_descriptions/date_asset_deleted.md) | ARS | Event based | ARS | Event based | |
| [date_asset_finalised](Data_field_descriptions/date_asset_finalised.md) | TBD | | | | |
| [date_asset_updated](Data_field_descriptions/date_asset_updated.md) | TBD | | | | See asset_updated_by |
| [date_metadata_created](Data_field_descriptions/date_metadata_created.md) | Ingestion client | Running IngestionClient | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call | |
| [date_metadata_updated](Data_field_descriptions/date_metadata_updated.md) | ARS | Event based | ARS | Event completion | |
| [date_metadata_uploaded](Data_field_descriptions/date_metadata_uploaded.md) | ARS | Event based | ARS | Event based | |
| [digitiser](Data_field_descriptions/digitiser.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | ARS | Upon creation / Upon integration creation / Upon ARS call |
| [external_publisher](Data_field_descriptions/external_publisher.md) | TBD | | | | |
| [file_format](Data_field_descriptions/file_format.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call | |
| [funding](Data_field_descriptions/funding.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call | |
| [institution](Data_field_descriptions/institution.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call | |
| [metadata_created_by](Data_field_descriptions/metadata_created_by.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call | |
| [metadata_updated_by](Data_field_descriptions/metadata_updated_by.md) | TBD | | | | |
| [metadata_uploaded_by](Data_field_descriptions/metadata_uploaded_by.md) | TBD | | | | |
| [multispecimen](Data_field_descriptions/multispecimen.md) | Pipeline | Running pipeline | ARS / Integration | Upon ARS call / Upon integration call | |
| [parent_guid](Data_field_descriptions/parent_guid.md) | Pipeline | Running pipeline | Integration / ARS | Upon integration creation / Upon ARS call | |
| [payload_type](Data_field_descriptions/payload_type.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file | | |
| [pipeline_name](Data_field_descriptions/pipeline_name.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file | | |
| [preparation_type](Data_field_descriptions/preparation_type.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call | |
| [pushed_to_specify_date](Data_field_descriptions/pushed_to_specify_date.md) | ARS | Event | ARS | Event | |
| [restricted_access](Data_field_descriptions/restricted_access.md) | TBD | | | | |
| [specimen_pid](Data_field_descriptions/specimen_pid.md) | TBD | TBD | | | |
| [status](Data_field_descriptions/status.md) | TBD | | | | This is our status for the asset, should begin population with ingestion server- or be removed. We dont use this status for anythng as is. |
| [tags](Data_field_descriptions/tags.md) | FREE FOR ALL TBD | | | | |
| [workstation_name](Data_field_descriptions/workstation_name.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Uponcreation / Upon integration creation / Upon ARS call | |



| Track Data Field name in json   | Written by          | When          | Saved where        | When       | Relevant into      |
|--------------------------------|---------------------|---------------|--------------------|------------|--------------------|
| [_id](Track_field_descriptions/_id.md) | Integration | Receiving metadata | Integration | Receiving metadata |  |
| [created_timestamp](Track_field_descriptions/created_timestamp.md) | Integration | Receiving metadata | Integration | Receiving metadata |  |
| [pipeline](Track_field_descriptions/pipeline.md) | Integration | Receiving metadata | Integration | Receiving metadata |  |
| [batch_list_name](Track_field_descriptions/batch_list_name.md) | Integration | Receiving metadata | Integration | Receiving metadata |  |
| x | d | x | d | x | d |
| [job_list](Track_field_descriptions/job_list.md) | Integration | Receiving metadata | Integration | Receiving metadata|  |
| [name](Track_field_descriptions/name.md) | Integration | Receiving metadata | Integration | Receiving metadata | Part of the object in job_list  |
| [status](Track_field_descriptions/status.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon integration call / Internal process | Part of the object in job_list |
| [priority](Track_field_descriptions/priority.md) | Integration | Receiving metadata | Integration | Receiving metadata | Part of the object in job_list |
| [job_start_time](Track_field_descriptions/job_start_time.md) | Integration | Upon integration call | Integration | Upon integration call | Part of the object in job_list |
| [hpc_job_id](Track_field_descriptions/hpc_job_id.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon integration call | Part of the object in job_list |
| x | d | x | d | x | d |
| [jobs_status](Track_field_descriptions/jobs_status.md) | Integration | Receiving metadata | Integration | Receiving metada / Upon integration call / Internal process |  |
| x | d | x | d | x | d |
| [file_list](Track_field_descriptions/file_list.md) | Integration | Receiving metadata | Integration | Receiving metada / Upon integration call |  |
| [name](Track_field_descriptions/name.md) | Integration | Receiving asset / Upon integration call | Integration | Receiving asset / Upon integration call | Part of the object in [file_list](Track_field_descriptions/file_list.md) |
| [type](Track_field_descriptions/type.md) | Integration | Receiving asset / Upon integration call | Integration | Receiving asset / Upon integration call | Part of the object in [file_list](Track_field_descriptions/file_list.md) |
| [time_added](Track_field_descriptions/time_added.md) | Integration | Receiving asset / Upon integration call | Integration | Receiving asset / Upon integration call | Part of the object in [file_list](Track_field_descriptions/file_list.md) |
| [check_sum](Track_field_descriptions/check_sum.md) | Integration | Receiving asset / Upon integration call | Integration | Receiving asset / Upon integration call | Part of the object in [file_list](Track_field_descriptions/file_list.md) |
| [file_size](Track_field_descriptions/file_size.md) | Integration | Receiving asset / Upon integration call | Integration | Receiving asset / Upon integration call | Part of the object in [file_list](Track_field_descriptions/file_list.md) |
| [ars_link](Track_field_descriptions/ars_link.md) | Integration | File uploaded ARS / Open share | Integration | File uploaded ARS / Open share | Part of the object in [file_list](Track_field_descriptions/file_list.md) |
| [erda_sync](Track_field_descriptions/erda_sync.md) | Integration | Upon ARS call / Upon integration call | Integration | Upon ARS call / Upon integration call | Part of the object in [file_list](Track_field_descriptions/file_list.md) |
| [deleted](Track_field_descriptions/deleted.md) | Integration | Upon ARS call | Integration | Upon ARS call | Part of the object in [file_list](Track_field_descriptions/file_list.md) |
| x | d | x | d | x | d |
| [files_status](Track_field_descriptions/files_status.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon integration call / Upon ARS call |  |
| [asset_size](Track_field_descriptions/asset_size.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon integration call / Upon ARS call |  |
| [proxy_path](Track_field_descriptions/proxy_path.md) | Integration | Receiving metadata | Integration | Upon ARS call open share |  |
| [hpc_ready](Track_field_descriptions/hpc_ready.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon integration call |  |
| [is_in_ars](Track_field_descriptions/is_in_ars.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon ARS call |  |
| [has_new_file](Track_field_descriptions/has_new_file.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon integration call |  |
| [has_open_share](Track_field_descriptions/has_open_share.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon ARS call |  |
| [erda_sync](Track_field_descriptions/erda_sync.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon ARS call |  |
| [update_metadata](Track_field_descriptions/update_metadata.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon integration call / Upon ARS call |  |
| t | h | e | e | n | d |
