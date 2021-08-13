import geopandas as gpd

eplison = 0.0000001

shp = gpd.read_file('/Users/shg096/Desktop/MERIT_Hydro/cat_fixed/cat_pfaf_74_MERIT_Hydro_v07_Basins_v01_bugfix1_fixed_test.shp')
shp = shp [shp['COMID']==74072024]
shp_temp = shp.buffer(-eplison, cap_style=2, join_style=2)
shp_temp = gpd.GeoDataFrame(shp.geometry.iloc[0])
shp_temp.columns = ['geometry']
shp_temp.set_geometry(col='geometry', inplace=True)
shp_temp ['A'] = shp_temp.area
shp_temp = shp_temp.sort_values(by='A',ascending=False)
#shp_temp = shp_temp.buffer(eplison, cap_style=2, join_style=2)
print(shp_temp)
shp.geometry.iloc[0]  = shp_temp.geometry.iloc[0]
print(shp)
shp.plot()
shp.to_file('/Users/shg096/Desktop/COMID_74072024.gpkg')
