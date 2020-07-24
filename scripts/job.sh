#!/bin/bash
#SBATCH --account=rpp-kshook
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=16G
#SBATCH --time=1-00:00           # time (DD-HH:MM)
#SBATCH --job-name=shapefilecorrection
#SBATCH --error=errors1

module load python/3.7  # load the python version

virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate

module load proj
pip install --no-index --upgrade pip
pip install --no-index pandas
pip install --no-index fiona
pip install --no-index shapely
pip install --no-index geopandas
pip install --no-index bs4
pip install --no-index urllib
pip install --no-index requests
pip install --no-index re
pip install --no-index glob
pip install --no-index time
pip install --no-index netCDF4
pip install --no-index numpy
pip install --no-index xarray
pip install --no-index os


chmod +x run.py
./run.py # run the scripts

deactivate

rm -rf $SLURM_TMPDIR/env
