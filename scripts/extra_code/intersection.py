from candex import *

path = '/Users/shg096/Desktop/MERIT_Hydro_basin_bugfixed_valid/'
basins = ['71','72','73','74','75','76','77','78','81','82','83','84','85','86'] # list of basins for NA and arctics

for basin in basins:
    shp1 = gpd.read_file (path+'cat_pfaf_'+basin+'_MERIT_Hydro_v07_Basins_v01_bugfix1_valid_poly.shp')
    #shp1.crs = {'init': 'epsg:4326', 'no_defs': True}
    shp1.crs = 'epsg:4326'
    shp1["lon_c"] = shp1.centroid.x # pass calculated centroid lon to the shp1
    shp1["lat_c"] = shp1.centroid.y # pass calculated centroid lat to the shp1
    print(shp1.crs)
    shp2 = gpd.read_file ('/Users/shg096/Desktop/era5_land_withArea.shp') # original /project/6008034/Model_Output/ClimateForcingData/ERA5_NA_shapefile_land_wsg84_withArea
    print(shp2.crs)
    shp_int = intersection_shp(shp1, shp2)
    shp_int = shp_int.rename(columns={"S_1_COMID" : "COMID", # hruId that is used as SUMMA computational units ID
                                      "S_1_lat_c" : "lat", # lon of hru
                                      "S_1_lon_c" : "lon", # lat of hru
                                      "S_2_shp_ID": "ERA5ID", # ERA5 grid ID, not used
                                      "S_2_lat"   : "ERA5lat", # lon of forcing grid to be read
                                      "S_2_lon"   : "ERA5lon", # lat of forcing grid to be read
                                      "AP1N"      : "ERA5W"}) # weight of each ERA5 grid in subbasin
    shp_int = shp_int.sort_values(by=['COMID'])
    shp_int.to_file(path+'cat_pfaf_'+basin+'_MERIT_Hydro_v07_Basins_v01_bugfix1_valid_poly_Era5.shp')
