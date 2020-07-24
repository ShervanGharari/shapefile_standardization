#!/cvmfs/soft.computecanada.ca/easybuild/software/2017/Core/python/3.7.4/bin/python

from shp_std_def import *

#############
#############
# INPUTS, Download of the shapefiles

IDs = ['21','22', '23', '24', '25','26','27','28','29']
#IDs = ['21']
http_path = 'http://hydrology.princeton.edu/data/mpan/for_martyn/'
path = '/Users/shg096/Desktop/test/'
path = '/project/6008034/Model_Output/ClimateForcingData/MERIT_Hydro_basin_bugfixed/'


#############
#############
# creat subfolders in folders
if os.path.exists(path+'cat'):
    os.mkdir(path+'cat')
if os.path.exists(path+'riv'):
    os.mkdir(path+'riv')
if os.path.exists(path+'hill'):
    os.mkdir(path+'hill')
if os.path.exists(path+'cat_step_0'):
    os.mkdir(path+'cat_step_0')
if os.path.exists(path+'cat_step_1'):
    os.mkdir(path+'cat_step_1')
if os.path.exists(path+'cat_fixed'):
    os.mkdir(path+'cat_fixed')
if os.path.exists(path+'hill_fixed'):
    os.mkdir(path+'hill_fixed')


#############
#############
# download the shapefiles
for ID in IDs:
    download(path+'cat/',
         http_path+'MERIT_Hydro_v07_Basins_v01_bugfix1/pfaf_level_02/',
        'cat',
        ID)
    download(path+'riv/',
         http_path+'MERIT_Hydro_v07_Basins_v01_bugfix1/pfaf_level_02/',
        'riv',
        ID)
    download(path+'hill/',
         http_path+'coastal_hillslopes/',
        'hill',
        ID)

#############
#############
# clean 2 prolematice shapes by removing holes
list_id = [11040208,56045327]  # the COMID IDs that result in shp_std_hard to crash hole outside shell
for ID in IDs:
    shp_std_light(path+'cat/cat_pfaf_'+ID+'_MERIT_Hydro_v07_Basins_v01_bugfix1.shp',
                  path+'cat_step_0/cat_pfaf_'+ID+'_MERIT_Hydro_v07_Basins_v01_bugfix1.shp',
                  path+'cat_step_0/cat_pfaf_'+ID+'_MERIT_Hydro_v07_Basins_v01_bugfix1_fixed.shp',
                 'COMID',
                  0.0000001,
                  list_id)


#############
#############
# correction of shapefiles
for ID in IDs:
    shp_std_hard(path+'cat_step_0/cat_pfaf_'+ID+'_MERIT_Hydro_v07_Basins_v01_bugfix1.shp',
                 path+'cat_step_1/cat_pfaf_'+ID+'_MERIT_Hydro_v07_Basins_v01_bugfix1_corr1.shp',
                 path+'cat_step_1/cat_pfaf_'+ID+'_MERIT_Hydro_v07_Basins_v01_bugfix1_corr1_hole.shp',
                 path+'cat_step_1/cat_pfaf_'+ID+'_MERIT_Hydro_v07_Basins_v01_bugfix1_corr1_log.txt',
                 'COMID',
                 0.0000000001)


#############
#############
# correction of shapefiles
list_id = [11038670,11040208,11035758,
           25000050,28045843,28046799,28047182,28050769,28059551,28064206,
           29020703,29028261,29034407,29048575,29050425,29071345,29092185,
           72055397,72055872,72058490,75027926,78012325,
           81033705,82042214,82041566,82002087,
           91025753,91035154,91035236,91035911]  # list of COMID that are still not valid based on QGIS
for ID in IDs:
    shp_std_light(path+'cat_step_1/cat_pfaf_'+ID+'_MERIT_Hydro_v07_Basins_v01_bugfix1_corr1.shp',
                  path+ 'cat_fixed/cat_pfaf_'+ID+'_MERIT_Hydro_v07_Basins_v01_bugfix1_corr2.shp',
                  path+ 'cat_fixed/cat_pfaf_'+ID+'_MERIT_Hydro_v07_Basins_v01_bugfix1_corr2_fixedshp.shp',
                 'COMID',
                 0.0000001,
                 list_id)

#############
#############
# correction the unresolved hillslope
for ID in IDs:
	shp_hill (path+'hill/hillslope_'+ID+'_clean.shp',
	          path+'cat/cat_pfaf_'+ID+'_MERIT_Hydro_v07_Basins_v01_bugfix1.shp',
	          path+'hill_fixed/hillslope_'+ID+'_clean.shp',
	          0.0000001)