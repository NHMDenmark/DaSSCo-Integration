| MOS Data Field name   | Written by          | When          | Saved where        | When       | Relevant into      |
|--------------------------------|---------------------|---------------|--------------------|------------|--------------------|
| [_id](MOS_field_descriptions/_id.md) | Integration server | Entry creation | Integration server MOS db | Received data from hpc script | This is the asset guid |
| [label](MOS_field_descriptions/label.md) | Barcode reader | Result from pipeline | Integration server MOS db | Received data from hpc script | Is this a label |
| [spid](MOS_field_descriptions/spid.md) | Integration server | Calculated for entry creation | Integration server MOS db | Received data from hpc script | Created from institution collection and barcode belonging to the asset |
| [disposable_id](MOS_field_descriptions/disposable_id.md) | Barcode reader | Result from pipeline | Integration server MOS db | Received data from hpc script | The id used by digitisers to show the connection |
| [unique_label_id](MOS_field_descriptions/unique_label_id.md) | Integration server | Calculated for entry creation | Integration server MOS db | Received data from hpc script | Created from workstation name, date asset was created and the disposable id |
| [label_connections](MOS_field_descriptions/label_connections.md) | Integration server | Entry creation, other connections found | Integration server MOS db | Received data from hpc script | List of asset guids for all asset sharing the unique label id |
