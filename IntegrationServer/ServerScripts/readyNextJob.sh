#!/bin/bash

id="$1"
jobname="$2"

# Run the MongoDB update operation using the mongosh shell
mongosh <<EOF > /dev/null
use test

db.track.updateOne(
    { _id: "$id" },
    { \$set: { "job_list.1.name": "$jobname", "job_list.1.status": "WAITING", "job_list.1.hpc_job_id": -9, "job_list.1.job_queued_time": null, "job_list.1.job_start_time": null } }
)

db.track.updateOne(
    { _id: "$id" },
    { \$set: { "jobs_list": "WAITING", "hpc_ready": "YES", "is_in_ars": "YES", "has_new_file": "NO", "has_open_share": "YES", "erda_sync": "YES", "update_metadata": "NO" } }
)
EOF

# Example use: bash assetLoader.sh asset_guid_here job_name_here
# The script sets the first job to be the desired job so it will be the first called to run by hpc, so make sure everything else is set up correctly to use that as job.
# The script will overwrite old job names and will not work with the assetLoader job since that requires hpc_ready to be NO.