| Meta Data Field name in json   | Written by          | When          | Saved where        | When       | Relevant into      |
|--------------------------------|---------------------|---------------|--------------------|------------|--------------------|
| [asset_created_by](Metadata_field_descriptions/asset_created_by.md) | ARS | Upon event | ARS | Upon ARS call | |
| [asset_deleted_by](Metadata_field_descriptions/asset_deleted_by.md) | ARS | Upon event | ARS | Upon ARS call | |
| [asset_guid](Metadata_field_descriptions/asset_guid.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration call / Upon ARS call |
| [asset_pid](Metadata_field_descriptions/asset_pid.md) | TBD | TBD | ARS / Integration | TBD | We have not figured out what this is or how its created yet. |
| [asset_subject](Metadata_field_descriptions/asset_subject.md) | Pipeline | Running pipeline | ARS / Integration | Upon ARS call / Upon Integration call | |
| [date_asset_taken](Metadata_field_descriptions/date_asset_taken.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call |
| [asset_updated_by](Metadata_field_descriptions/asset_updated_by.md) | TBD | TBD | TBD | TBD | Decision needs to be made on this field. Should it be a list and if so how should it map with date_asset_updated |
| [audited](Metadata_field_descriptions/audited.md) | TBD | | | | |
| [audited_by](Metadata_field_descriptions/audited_by.md) | TBD | | | | |
| [audited_date](Metadata_field_descriptions/audited_date.md) | TBD | | | | |
| [barcode](Metadata_field_descriptions/barcode.md) | Pipeline | Running pipeline | Integration / ARS | Upon integration call / Upon ARS call | |
| [collection](Metadata_field_descriptions/collection.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call |
| [date_asset_created](Metadata_field_descriptions/date_asset_created.md) | ARS | Upon event | ARS | Upon ARS call | Stamp for creation with ARS |
| [date_asset_deleted](Metadata_field_descriptions/date_asset_deleted.md) | ARS | Event based | ARS | Event based | |
| [date_asset_finalised](Metadata_field_descriptions/date_asset_finalised.md) | TBD | | | | |
| [date_asset_updated](Metadata_field_descriptions/date_asset_updated.md) | TBD | | | | See asset_updated_by |
| [date_metadata_created](Metadata_field_descriptions/date_metadata_created.md) | Ingestion client | Running IngestionClient | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call | |
| [date_metadata_updated](Metadata_field_descriptions/date_metadata_updated.md) | ARS | Event based | ARS | Event completion | |
| [date_metadata_uploaded](Metadata_field_descriptions/date_metadata_uploaded.md) | ARS | Event based | ARS | Event based | |
| [digitiser](Metadata_field_descriptions/digitiser.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | ARS | Upon creation / Upon integration creation / Upon ARS call |
| [external_publisher](Metadata_field_descriptions/external_publisher.md) | TBD | | | | |
| [file_format](Metadata_field_descriptions/file_format.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call | |
| [funding](Metadata_field_descriptions/funding.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call | |
| [institution](Metadata_field_descriptions/institution.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call | |
| [metadata_created_by](Metadata_field_descriptions/metadata_created_by.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call | |
| [metadata_updated_by](Metadata_field_descriptions/metadata_updated_by.md) | TBD | | | | |
| [metadata_uploaded_by](Metadata_field_descriptions/metadata_uploaded_by.md) | TBD | | | | |
| [multispecimen](Metadata_field_descriptions/multispecimen.md) | Pipeline | Running pipeline | ARS / Integration | Upon ARS call / Upon integration call | |
| [parent_guid](Metadata_field_descriptions/parent_guid.md) | Pipeline | Running pipeline | Integration / ARS | Upon integration creation / Upon ARS call | |
| [payload_type](Metadata_field_descriptions/payload_type.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file | | |
| [pipeline_name](Metadata_field_descriptions/pipeline_name.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file | | |
| [preparation_type](Metadata_field_descriptions/preparation_type.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call | |
| [pushed_to_specify_date](Metadata_field_descriptions/pushed_to_specify_date.md) | ARS | Event | ARS | Event | |
| [restricted_access](Metadata_field_descriptions/restricted_access.md) | TBD | | | | |
| [specimen_pid](Metadata_field_descriptions/specimen_pid.md) | TBD | TBD | | | |
| [status](Metadata_field_descriptions/status.md) | TBD | | | | This is our status for the asset, should begin population with ingestion server- or be removed. We dont use this status for anythng as is. |
| [tags](Metadata_field_descriptions/tags.md) | FREE FOR ALL TBD | | | | |
| [workstation_name](Metadata_field_descriptions/workstation_name.md) | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Uponcreation / Upon integration creation / Upon ARS call | |
