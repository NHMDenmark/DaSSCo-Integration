| Meta Data Field name in json   | Written by          | When          | Saved where        | When       | Relevant into      |
|--------------------------------|---------------------|---------------|--------------------|------------|--------------------|
| asset_created_by               | ARS                 | Upon event    | ARS                | Upon ARS call |                    |
| asset_deleted_by               | ARS                 | Upon event    | ARS                | Upon ARS call |                    |
| asset_guid                     | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration call / Upon ARS call |
| asset_pid                      | TBD                    |   TBD            | ARS / Integration                  | TBD           | We have not figured out what this is or how its created yet.                    |
| asset_subject                  | Pipeline            | Running pipeline | ARS / Integration               | Upon ARS call / Upon Integration call |                    |
| date_asset_taken               | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call |
| asset_updated_by               | TBD                     |      TBD         | TBD                | TBD           | Decision needs to be made on this field. Should it be a list and if so how should it map with date_asset_updated                   | 
| audited                        | TBD                 |               |                    |            |                    |
| audited_by                     | TBD                 |               |                    |            |                    |
| audited_date                   | TBD                 |               |                    |            |                    |
| barcode                        | Pipeline            | Running pipeline | Integration / ARS                | Upon integration call / Upon ARS call |                    |
| collection                     | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | Upon creation / Upon integration creation / Upon ARS call |
| date_asset_created             | ARS                | Upon event              | ARS                   | Upon ARS call           | Stamp for creation with ARS                   |
| date_asset_deleted             | ARS                 | Event based              | ARS                   | Event based           |                    |
| date_asset_finalised           | TBD                 |               |                    |            |                    |
| date_asset_updated             | TBD                 |               |                    |            | See asset_updated_by                   |
| date_metadata_created          | Ingestion client               | Running IngestionClient              | Metadata file / Integration / ARS                   | Upon creation / Upon integration creation / Upon ARS call           |                    |
| date_metadata_updated          | ARS       | Event based              | ARS                   | Event completion           |                    |
| date_metadata_uploaded         | ARS                 | Event based              | ARS                   | Event based           |                    |
| digitiser                      | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS | ARS | Upon creation / Upon integration creation / Upon ARS call  |
| external_publisher             | TBD                 |               |                    |            |                    |
| file_format                    | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS |  Upon creation / Upon integration creation / Upon ARS call | |
| funding                        | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS |  Upon creation / Upon integration creation / Upon ARS call | |
| institution                    | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS |  Upon creation / Upon integration creation / Upon ARS call | |
| metadata_created_by            | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS |  Upon creation / Upon integration creation / Upon ARS call | |
| metadata_updated_by            | TBD                 |               |                    |            |                     |
| metadata_uploaded_by          | TBD                 |               |                    |            |                    |
| multispecimen                  | Pipeline            | Running pipeline | ARS / Integration               | Upon ARS call / Upon integration call |                    |
| parent_guid                    | Pipeline            | Running pipeline | Integration / ARS |  Upon integration creation / Upon ARS call | |
| payload_type                   | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file |  |
| pipeline_name                  | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file |  |
| preparation_type               | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS |  Upon creation / Upon integration creation / Upon ARS call | |
| pushed_to_specify_date         | ARS                 | Event              | ARS                   | Event            |                    |
| restricted_access              | TBD                 |               |                    |            |                    |
| specimen_pid                   | TBD                 | TBD              |                    |            |                    |
| status                         | TBD                    |               |                    |            | This is our status for the asset, should begin population with ingestion server- or be removed. We dont use this status for anythng as is.                   |
| tags                           | FREE FOR ALL TBD                    |               |                    |            |                    |
| workstation_name               | IngestionClient for uploaded assets; pipeline for derivatives | Running IngestionClient/pipeline | Metadata file / Integration / ARS |  Upon creation / Upon integration creation / Upon ARS call | |
| _id | Integration | Receiving metadata | Integration | Receiving metada |  |
| created_timestamp | Integration | Receiving metadata | Integration | Receiving metada |  |
| pipeline | Integration | Receiving metadata | Integration | Receiving metada |  |
| batch_list_name | Integration | Receiving metadata | Integration | Receiving metada |  |
| job_list | Integration | Receiving metadata | Integration | Receiving metada|  |
| name | Integration | Receiving metadata | Integration | Receiving metada | Part of the object in job_list  |
| status | Integration | Receiving metadata | Integration | Receiving metada / Upon integration call / Internal process | Part of the object in job_list |
| priority | Integration | Receiving metadata | Integration | Receiving metada | Part of the object in job_list |
| job_start_time | Integration | Upon integration call | Integration | Upon integration call | Part of the object in job_list |
| hpc_job_id | Integration | Receiving metadata | Integration | Receiving metada / Upon integration call | Part of the object in job_list |
| jobs_status | Integration | Receiving metadata | Integration | Receiving metada / Upon integration call / Internal process |  |
| file_list | Integration | Receiving metadata | Integration | Receiving metada / Upon integration call |  |
| files_status | Integration | Receiving metadata | Integration | Receiving metada / Upon integration call / Upon ARS call |  |
| asset_size | Integration | Receiving metadata | Integration | Receiving metada / Upon integration call / Upon ARS call |  |
| hpc_ready | Integration | Receiving metadata | Integration | Receiving metada / Upon integration call |  |
| is_in_ars | Integration | Receiving metadata | Integration | Receiving metada / Upon ARS call |  |
| has_new_file | Integration | Receiving metadata | Integration | Receiving metada / Upon integration call |  |
| has_open_share | Integration | Receiving metadata | Integration | Receiving metada / Upon ARS call |  |
| erda_sync | Integration | Receiving metadata | Integration | Receiving metada / Upon ARS call |  |
| update_metadata | Integration | Receiving metadata | Integration | Receiving metada / Upon integration call / Upon ARS call |  |
| x | d | x | d | x | d |


