#!/bin/bash
#SBATCH --account=rpp-kshook
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=2G
#SBATCH --time=1-00:00           # time (DD-HH:MM)
#SBATCH --job-name=shapefilecorrection  
#SBATCH --error=errors1

module load python/3.5  # load the python version

virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate

pip install --no-index --upgrade pip
pip install --no-index pandas
pip install --no-index shapely
pip install --no-index geopandas

chmod +x run.py
./run.py # run the scripts

deactivate

rm -rf $SLURM_TMPDIR/env