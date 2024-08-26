| Track Data Field name   | Written by          | When          | Saved where        | When       | Relevant into      |
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
| [asset_type](Track_field_descriptions/asset_type.md) | Integration | Receiving metadata | Integration | Upon ARS call | Asset type enum |
| [hpc_ready](Track_field_descriptions/hpc_ready.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon integration call |  |
| [is_in_ars](Track_field_descriptions/is_in_ars.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon ARS call |  |
| [has_new_file](Track_field_descriptions/has_new_file.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon integration call |  |
| [has_open_share](Track_field_descriptions/has_open_share.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon ARS call |  |
| [erda_sync](Track_field_descriptions/erda_sync.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon ARS call |  |
| [update_metadata](Track_field_descriptions/update_metadata.md) | Integration | Receiving metadata | Integration | Receiving metadata / Upon integration call / Upon ARS call |  |
| [temporary_files_ndrive](Track_field_descriptions/temporary_files_ndrive.md) | Integration | Receiving asset from ndrive | Integration | Processing asset files  | Temporary field that gets deleted at the end of the pipeline |
| [temporary_path_ndrive](Track_field_descriptions/temporary_path_ndrive.md) | Integration | Receiving asset from ndrive | Integration | Processing asset files  | Temporary field that gets deleted at the end of the pipeline |
| [temporary_files_local](Track_field_descriptions/temporary_files_local) | Integration | Receiving asset from ndrive | Integration | Processing asset files  | Temporary field that gets deleted at the end of the pipeline |
| [temporary_path_local](Track_field_descriptions/temporary_path_local.md) | Integration | Receiving asset from ndrive | Integration | Processing asset files  | Temporary field that gets deleted at the end of the pipeline |
| t | h | e | e | n | d |