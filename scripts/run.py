#!/cvmfs/soft.computecanada.ca/easybuild/software/2017/Core/python/3.7.4/bin/python

from shp_std_def import *

path = '/project/6008034/Model_Output/ClimateForcingData/MERIT_Hydro_basin_original/'
field_name = 'COMID'
tolerance = 0.1 # 0.1 m2 in equal area projection
extension = '.shp'

# North America Domain Shapes
#shp_std('cat_pfaf_1_MERIT_Hydro_v07_Basins_v01', extension, path, field_name, tolerance)
#shp_std('cat_pfaf_2_MERIT_Hydro_v07_Basins_v01', extension, path, field_name, tolerance)
#shp_std('cat_pfaf_3_MERIT_Hydro_v07_Basins_v01', extension, path, field_name, tolerance)
#shp_std('cat_pfaf_4_MERIT_Hydro_v07_Basins_v01', extension, path, field_name, tolerance)
#shp_std('cat_pfaf_5_MERIT_Hydro_v07_Basins_v01', extension, path, field_name, tolerance)
#shp_std('cat_pfaf_6_MERIT_Hydro_v07_Basins_v01', extension, path, field_name, tolerance)
shp_std('cat_pfaf_7_MERIT_Hydro_v07_Basins_v01', extension, path, field_name, tolerance)
#shp_std('cat_pfaf_8_MERIT_Hydro_v07_Basins_v01', extension, path, field_name, tolerance)
