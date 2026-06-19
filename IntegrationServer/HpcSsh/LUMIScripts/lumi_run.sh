#!/bin/bash
set -e

# ---- LUMI environment setup ----
module load LUMI
module load lumi-container-wrapper

set -a
source /scratch/project_465002693/slurm_tykky/ucloud_copy/DaSSCo-Image-Refinery/.env
set +a

cd /scratch/project_465002693/slurm_tykky/hpc-container-wrapper || exit 1
source etc/profile.d/tykky.sh

tykky activate venv/

cd /scratch/project_465002693/slurm_tykky/ucloud_copy/DaSSCo-Image-Refinery/src/dasscorefinery/ || exit 1

# ---- Run dynamic command ----
exec "$@"