import pandas as pd
from shapely.ops import unary_union
import shapely
import geopandas as gpd


def shp_std(name_of_file, name_of_ext, name_of_dir, ID_field, area_tolerance):
    """
    @ author:                  Shervan Gharari
    @ Github:                  https://github.com/ShervanGharari/shapefile_standardization
    @ author's email id:       sh.gharari@gmail.com
    @license:                  MIT

    This function gets name of a shapefile, its directory, and its extensions (such as gpkg or shp) and
    save a stadard shapefile. if presence it also save the holes of a shapefile
    
    Arguments
    ---------
    name_of_file: string, the name of the shp file
    name_of_ext: string, the name of the shp file format (".shp" or ".gpkg")
    name_of_dir: string, the name of directory where the shp file is located
    ID_field: string, the name of the field in the original shapefile that is used for keeping track of holes
    area_tolerance: float; the tolerance to compare area before and after correction and report differences
    
    Returns
    -------
    
    
    Saves Files
    -------
    a shp file that includes corrected polygones
    a shp file that includes possible holes in the polygones which can be taken out from the polygon shp
    a log file in the same folder descringin the invalid shapefiles
    """

    shp_original = gpd.read_file(name_of_file+name_of_ext)
    shp_poly     = shp_original
    shp_hole     = None
    
    print(shp_original.shape[0])
    
    
    logfile = open(name_of_dir+name_of_file+'.txt',"w") # preparing the log file to write
    
    number_invalid = 0 # counter for invalid shapes
    number_resolved = 0 # counter for resolved invalid shapes
    number_not_resolved = 0 # counter for not resolved invalid shapes
    
    for index, _ in shp_original.iterrows():

        print(index)
        polys = shp_original.geometry.iloc[index] # get the shape
        area_before = polys.area # area before changes
        
        invalid = False # initializing invalid as false
        # check if the shapefile is valid
        if polys.is_valid is False: # check if the geometry is invalid
            number_invalid = number_invalid + 1
            invalid = True
            str_temp = str(number_invalid)+". shape with ID "+str(shp_original[ID_field].iloc[index])+\
            " is not valid"
            logfile.write(str_temp)

        # put the shape into a Polygon or MultiPolygon
        if polys.type is 'Polygon':
            print(polys.type)
            shp_temp = gpd.GeoSeries(polys) # convert multipolygon to a shapefile with polygons only
            #shp_temp.columns = ['geometry'] # naming geometry column
            shp_temp = gpd.GeoDataFrame(shp_temp) # convert multipolygon to a shapefile with polygons only
            shp_temp.columns = ['geometry'] # naming geometry column
            print(shp_temp)
        if polys.type is 'MultiPolygon':
            print(polys.type)
            shp_temp = gpd.GeoDataFrame(polys) # convert multipolygon to a shapefile with polygons only
            shp_temp.columns = ['geometry'] # naming geometry column
            print(shp_temp)

        has_holes = False # initializing hole as false
        shp_temp['CCW'] = 0 # initialize check for couterclockwise (holes)
        for index1, _ in shp_temp.iterrows(): #loop over polygone of one element
            poly = shp_temp.geometry.iloc[index1] # get the geometry of polygon
            if poly.exterior.is_ccw is True: # then the polgone is a hole
                shp_temp['CCW'].iloc[index1] = 1 # set the hole flag to 1
                shp_temp['geometry'].iloc[index1] = shapely.geometry.polygon.orient(poly, sign = +1) # +1 make it CCW
                print(shp_temp['geometry'].iloc[index1])
                has_holes = True

        shp_temp_polys = shp_temp[shp_temp.CCW ==0] # get the polyons that are not couter clockwise
        shp_temp_polys['dis'] = 0 # add a field for desolve
        shp_temp_polys = shp_temp_polys.dissolve(by='dis') # to one multipolygon
        polys_temp = shp_temp_polys.geometry.iloc[0] # update the shapefile on that
        polys_temp = unary_union(polys_temp) # unify all the polygons into a multipolygons
        shp_poly.geometry.iloc[index] = polys_temp.buffer(0) # fix the issue by buffer(0)
        area_after = shp_poly.geometry.iloc[index].area # area after changes
        
        # check if the shapefile becomes valid
        if shp_poly.geometry.iloc[index].is_valid is True and invalid is True: # check if the geometry is invalid
            str_temp = " and becomes valid \n"
            logfile.write(str_temp)
            number_resolved = number_resolved + 1
        if shp_poly.geometry.iloc[index].is_valid is False and invalid is True: # check if the geometry is invalid
            str_temp = " and does not become valid; please check the shape \n"
            logfile.write(str_temp)
            number_not_resolved = number_not_resolved + 1

        if has_holes is True:
            shp_temp_holes = shp_temp[shp_temp.CCW ==1]
            shp_temp_holes['dis'] = 0
            shp_temp_holes = shp_temp_holes.dissolve(by='dis') # to one multipolyno
            shp_temp_holes[ID_field] = shp_original[ID_field].iloc[index]
            if shp_hole is None:
                shp_hole = shp_temp_holes
            else:
                shp_hole = gpd.GeoDataFrame( pd.concat([shp_hole, shp_temp_holes], ignore_index=True) )
            str_temp = "Shape has a hole \n"
            logfile.write(str_temp)
        
        if abs(area_before-area_after)>area_tolerance: # tolernace can be different based on projection
            str_temp = "shape area changes abs("+str(area_before)+"-"+str(area_after)+") = "+\
            str(area_before-area_after)+" \n"
            logfile.write(str_temp)
         

    shp_poly.to_file(name_of_dir+name_of_file+'_poly.shp')
    if shp_hole is not None:
        shp_hole.to_file(name_of_dir+name_of_file+'_hole.shp') #save any hole to check
        
    str_temp = "Total number of shapes = "+str(shp_original.shape[0])+" \n"
    str_temp = "Total number of invalid shapes = "+str(number_invalid)+" \n"
    str_temp = "Total number of resolved invalid shapes = "+str(number_resolved)+" \n"
    str_temp = "Total number of not resolved invalid shapes = "+str(number_not_resolved)+" \n"
    logfile.write(str_temp)
    logfile.close() # close the log gile
    
    
