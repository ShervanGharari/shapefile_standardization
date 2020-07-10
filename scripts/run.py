#!/cvmfs/soft.computecanada.ca/easybuild/software/2017/Core/python/3.5.4/bin/python

from shap_std_def.py import shp_std

path = '/project/6008034/Model_Output/ClimateForcingData/MERIT_Hydro_basin/'
field_name = 'segId'
tolerance = 0.1 # 0.1 m2 in equal area projection
stem = 'catEndoMERITpfaf_' # coomon part of the file names
extension = '.gpkg'

shp_std(stem+'71', extension, path, field_name, tolerance)
shp_std(stem+'72', extension, path, field_name, tolerance)
shp_std(stem+'73', extension, path, field_name, tolerance)
shp_std(stem+'74', extension, path, field_name, tolerance)
shp_std(stem+'75', extension, path, field_name, tolerance)
shp_std(stem+'76', extension, path, field_name, tolerance)
shp_std(stem+'77', extension, path, field_name, tolerance)
shp_std(stem+'78', extension, path, field_name, tolerance)
shp_std(stem+'81', extension, path, field_name, tolerance)
shp_std(stem+'82', extension, path, field_name, tolerance)
shp_std(stem+'83', extension, path, field_name, tolerance)
