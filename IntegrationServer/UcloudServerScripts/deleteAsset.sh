#!/bin/bash

id="$1"

mongosh <<EOF > /dev/null
use test
db.track.deleteOne(
    { _id: "$id"}
)
db.metadata.deleteOne(
    { _id: "$id"}
)
EOF

# Example use bash deleteAsset.sh asset_guid_here
<<<<<<< HEAD
# Deletes an asset from both the metadata and track collections.
=======
# Deletes an asset from both the metadata and track collections.
>>>>>>> origin
