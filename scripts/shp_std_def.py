import pandas as pd
from shapely.ops import unary_union
import shapely
import geopandas as gpd
from shapely.geometry import Polygon
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import requests
import re


def download(des_loc,
                   http_page,
                   str1,
                   str2):
    """
    @ author:                  Shervan Gharari
    @ Github:                  https://github.com/ShervanGharari/shapefile_standardization
    @ author's email id:       sh.gharari@gmail.com
    @license:                  MIT

    This function gets name of a http and two str in the name of the link and save them in provided destnation
    

    Arguments
    ---------
    des_loc: string, the name of the source file including path and extension
    http_page: string, the name of the corresponding catchment (subbasin) for the unresolved hills
    str1: string, a part of the link name to filter
    str2: string, a second part of the link name to filter
    

    Returns
    -------


    Saves Files
    -------
    downlaod the files from the websites and save them in the correct location
    """

    # first get all the links in the page
    req = Request(http_page)
    html_page = urlopen(req)
    soup = BeautifulSoup(html_page, "lxml")
    links = []
    for link in soup.findAll('a'):
        links.append(link.get('href'))

    # specify the link to be downloaded
    link_to_download = []
    for link in links:
        # if "hillslope" in link and "clean" in link: # links that have cat_pfaf and Basins in them
        if str1 in link and str2 in link: # links that have cat_pfaf and Basins in them
            link_to_download.append(link)
            print(link)

    # creat urls to download
    urls =[]
    for file_name in link_to_download:
        urls.append(http_page+file_name) # link of the page + file names
        print(http_page+file_name)
    print(urls)

    # loop to download the data
    for url in urls:
        name = url.split('/')[-1] # get the name of the file at the end of the url to download
        r = requests.get(url) # download the URL
        # print the specification of the download 
        print(r.status_code, r.headers['content-type'], r.encoding)
        # if download successful the statuse code is 200 then save the file, else print what was not downloaded
        if r.status_code == 200:
            print('download was successful for '+url)
            with open(des_loc+name, 'wb') as f:
                f.write(r.content)
        else:
            print('download was not successful for '+url)


def shp_std_costal(name_of_source_file,
                   name_of_cat_file,
                   name_of_result_file,
                   epsilon):
    """
    @ author:                  Shervan Gharari
    @ Github:                  https://github.com/ShervanGharari/shapefile_standardization
    @ author's email id:       sh.gharari@gmail.com
    @license:                  MIT

    This function gets name of a shapefile and remove inernal holes

    Arguments
    ---------
    name_of_source_file: string, the name of the source file including path and extension
    name_of_cat_file: string, the name of the corresponding catchment (subbasin) for the unresolved hills
    name_of_result_file: string, the name of the file that includes fixed shapes including path and extension
    

    Returns
    -------


    Saves Files
    -------
    a shp file that includes corrected polygones
    a possible shapefile that includes the fixed shapes
    """
    
    shp = gpd.read_file(name_of_source_file)
    cat1 = gpd.read_file(name_of_cat_file)


    ## STEP1, load a shapefile, and find its intesection with itself. there are
    ## there should be some holes in the shapefile. the holes are given as a separaete shape

    shp_temp = gpd.overlay(shp, shp, how='intersection')
    shp_temp = shp_temp [shp_temp.FID_1 != shp_temp.FID_2]
    #shp_temp.to_file('temp1.shp')
    shp_temp = gpd.overlay(shp, shp_temp, how='difference')
    #shp_temp.to_file('temp2.shp')

    ## STEP2, remove possible cat from the unresolved costal hillslope
    shp_temp = gpd.overlay(shp_temp, cat1, how='difference')
    #shp_temp.to_file('temp3.shp')

    ## STEP3, break the polygons into separate multipolygons, remove the links (lines)
    shp_temp = shp_temp.buffer(-epsilon).buffer(epsilon)
    shp_temp.to_file('temp4.shp')

    ## STEP4, break the polygones into separete shape in a shapefile
    shp = gpd.read_file('temp4.shp')

    shp_all = None

    for index, _ in shp.iterrows():

        polys = shp.geometry.iloc[index] # get the shape

        if polys.type is 'Polygon':
            shp_temp = gpd.GeoSeries(polys) # convert multipolygon to a shapefile with polygons only
            shp_temp = gpd.GeoDataFrame(shp_temp) # convert multipolygon to a shapefile with polygons only
            shp_temp.columns = ['geometry'] # naming geometry column
        if polys.type is 'MultiPolygon':
            shp_temp = gpd.GeoDataFrame(polys) # convert multipolygon to a shapefile with polygons only
            shp_temp.columns = ['geometry'] # naming geometry column

        if shp_all is None:
            shp_all = shp_temp
        else:
            shp_all = shp_all.append(shp_temp)

    shp_all.to_file(name_of_result_file)


def extract_poly_coords(geom):
    if geom.type == 'Polygon':
        exterior_coords = geom.exterior.coords[:]
        interior_coords = []
        for interior in geom.interiors:
            interior_coords += interior.coords[:]
    elif geom.type == 'MultiPolygon':
        exterior_coords = []
        interior_coords = []
        for part in geom:
            epc = extract_poly_coords(part)  # Recursive call
            exterior_coords += epc['exterior_coords']
            interior_coords += epc['interior_coords']
    else:
        raise ValueError('Unhandled geometry type: ' + repr(geom.type))
    return {'exterior_coords': exterior_coords,
            'interior_coords': interior_coords}


def shp_std_2(name_of_source_file,
              name_of_result_file,
              name_of_result_file_fixed_shapes,
              ID_field,
              epsilon,
              list_id):
    """
    @ author:                  Shervan Gharari
    @ Github:                  https://github.com/ShervanGharari/shapefile_standardization
    @ author's email id:       sh.gharari@gmail.com
    @license:                  MIT

    This function gets name of a shapefile and remove inernal holes

    Arguments
    ---------
    name_of_source_file: string, the name of the source file including path and extension
    name_of_result_file: string, the name of the final file including path and extension
    name_of_result_file_fixed_shapes: string, the name of the file that includes fixed shapes including path and extension
    name_of_log_file: string, the name of the text log file with path and txt extension
    ID_field: string, the name of the field in the original shapefile that is used for keeping track of holes
    epsilon: real, the minimum distance for buffer operation
    list_id: list of shape IDs that should be corrected

    Returns
    -------


    Saves Files
    -------
    a shp file that includes corrected polygones
    a possible shapefile that includes the fixed shapes
    """
    
    # load the shapefile
    shp = gpd.read_file(src_dir_name+src_file_name)
    print(shp.shape[0])
    shp_new = shp # pass the shape to a new shape
    shp_new['flag'] = 0 # add flag for the shapefile ids that are resolved
    
    for ID in list_id:
        for index, _ in shp.iterrows():
            if shp[ID_field][index] == ID:
                shp_temp = shp.geometry.iloc[index]
                shp_temp = shp_temp.buffer(epsilon) # to amalgamate the polygones of multipolygons into a polygon
                shp_temp = gpd.GeoSeries(shp_temp) # to geoseries
                shp_temp = gpd.GeoDataFrame(shp_temp) # to geoframe
                shp_temp.columns = ['geometry'] # call the colomn geometry
                poly = shp_temp.geometry.iloc[0] # get the polygone from the shapefile
                A = extract_poly_coords(poly) # extract the exterior
                outer = A['exterior_coords'] # pass the exterior
                poly_new = Polygon (outer) # make a polygone out of the 
                shp_new.geometry.iloc[index] = poly_new # pass the geometry to the new shapefile
                shp_new['flag'].iloc[index] = 1 # put flag as 1
                shp_temp = shp_new.geometry.iloc[index] # get the shape
                shp_temp = shp_temp.buffer(-epsilon) # redo the buffer
                shp_temp = gpd.GeoSeries(shp_temp) # to geoseries
                shp_temp = gpd.GeoDataFrame(shp_temp) # geo dataframe
                shp_temp.columns = ['geometry'] # name the column as geometry
                shp_new.geometry.iloc[index] = shp_temp.geometry.iloc[0] # pass that to the new shape

    shp_new = shp_new [shp_new.flag ==1] # get the shapes that flag are 1
    if not shp_new.empty:
        shp_new = shp_new.drop(columns=['flag'])
        shp_diff = gpd.overlay(shp, shp_new, how='difference') # get the difference
        shp_all = shp_new.append(shp_diff) # append the fixed shapefiles to the diff
        if shp.shape[0] == shp_all.shape[0]:
            shp_new.to_file(final_dir_name+final_file_name+'fexed_shps') #saved the fixed shapefile
            shp_all.to_file(final_dir_name+final_file_name) # save the entire
        else:
            print('input output have different lenght; check')

def shp_std_1(name_of_source_file,
            name_of_result_file,
            name_of_result_file_holes,
            name_of_log_file,
            ID_field,
            area_tolerance):
    """
    @ author:                  Shervan Gharari
    @ Github:                  https://github.com/ShervanGharari/shapefile_standardization
    @ author's email id:       sh.gharari@gmail.com
    @license:                  MIT

    This function gets name of a shapefile, its directory, and its extensions (such as gpkg or shp) and
    save a stadard shapefile. if presence it also save the holes of a shapefile

    Arguments
    ---------
    name_of_source_file: string, the name of the source file including path and extension
    name_of_result_file: string, the name of the final file including path and extension
    name_of_result_file_holes: string, the name of the file that includes holes including path and extension
    name_of_log_file: string, the name of the text log file with path and txt extension
    ID_field: string, the name of the field in the original shapefile that is used for keeping track of holes
    area_tolerance: float; the tolerance to compare area before and after correction and report differences

    Returns
    -------


    Saves Files
    -------
    a shp file that includes corrected polygones
    a possible shapefile that includes the removed problematice holes
    a log file in the same folder descringin the invalid shapefiles
    """

    shp_original = gpd.read_file(name_of_source_file)
    shp_poly     = shp_original
    shp_hole     = None

    logfile = open(name_of_log_file,"w") # preparing the log file to write

    number_invalid = 0 # counter for invalid shapes
    number_resolved = 0 # counter for resolved invalid shapes
    number_not_resolved = 0 # counter for not resolved invalid shapes

    for index, _ in shp_original.iterrows():

        # initialization
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
            # print(polys.type)
            shp_temp = gpd.GeoSeries(polys) # convert multipolygon to a shapefile with polygons only
            #shp_temp.columns = ['geometry'] # naming geometry column
            shp_temp = gpd.GeoDataFrame(shp_temp) # convert multipolygon to a shapefile with polygons only
            shp_temp.columns = ['geometry'] # naming geometry column
            #print(shp_temp)
        if polys.type is 'MultiPolygon':
            # print(polys.type)
            shp_temp = gpd.GeoDataFrame(polys) # convert multipolygon to a shapefile with polygons only
            shp_temp.columns = ['geometry'] # naming geometry column
            #print(shp_temp)

        has_holes = False # initializing hole as false
        shp_temp['CCW'] = 0 # initialize check for couterclockwise (holes)
        for index1, _ in shp_temp.iterrows(): #loop over polygone of one element
            poly = shp_temp.geometry.iloc[index1] # get the geometry of polygon
            if poly.exterior.is_ccw is True: # then the polgone is a hole
                shp_temp['CCW'].iloc[index1] = 1 # set the hole flag to 1
                shp_temp['geometry'].iloc[index1] = shapely.geometry.polygon.orient(poly, sign = +1) # +1 make it CCW
                #print(shp_temp['geometry'].iloc[index1])
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


    shp_poly.to_file(name_of_result_file)
    if shp_hole is not None:
        shp_hole.to_file(name_of_result_file_holes) #save any hole to check

    str_temp = "Total number of shapes = "+str(shp_original.shape[0])+" \n"
    logfile.write(str_temp)
    str_temp = "Total number of invalid shapes = "+str(number_invalid)+" \n"
    logfile.write(str_temp)
    str_temp = "Total number of resolved invalid shapes = "+str(number_resolved)+" \n"
    logfile.write(str_temp)
    str_temp = "Total number of not resolved invalid shapes = "+str(number_not_resolved)+" \n"
    logfile.write(str_temp)
    logfile.close() # close the log gile
