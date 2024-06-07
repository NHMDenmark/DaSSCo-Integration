#!/bin/bash

id="$1"

# Run the MongoDB update operation using the mongosh shell
mongosh <<EOF > /dev/null
use test

db.track.updateOne(
    { _id: "$id" },
    { \$set: { "job_list.0.name": "assetLoader", "job_list.0.status": "WAITING", "job_list.0.hpc_job_id": -9, "job_list.0.job_queued_time": null, "job_list.0.job_start_time": null } }
)

db.track.updateOne(
    { _id: "$id" },
    { \$set: { "jobs_list": "WAITING", "hpc_ready": "NO", "is_in_ars": "YES", "has_new_file": "NO", "has_open_share": "YES", "erda_sync": "YES", "update_metadata": "NO" } }
)
EOF

# Example use: bash assetLoader.sh asset_guid_here
# The script sets the first job to be the assetLoader so make sure everything else is set up correctly to use that as job.
