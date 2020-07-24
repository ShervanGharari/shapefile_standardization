import pandas as pd
from shapely.ops import unary_union
import shapely
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.geometry import Point
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import requests
import re
import glob
import time
import netCDF4 as nc4
import numpy as np
import pandas as pd
import xarray as xr
import os



def remove_dublicate_point(poly):
    """
    @ author:                  Shervan Gharari
    @ Github:                  https://github.com/ShervanGharari/shapefile_standardization
    @ author's email id:       sh.gharari@gmail.com
    @license:                  MIT
    
    This function gets a shapely polygon and remove dublicated point there
    

    Arguments
    ---------
    poly: shapely polygon, the input shapely polygon
    

    Returns
    -------


    Saves Files
    -------
    downlaod the files from the websites and save them in the correct location
    
    """
    A = 10000000
    x, y = poly.exterior.coords.xy
    X  = np.floor(np.array(x)*A)/A
    Y  = np.floor(np.array(y)*A)/A
    X = np.transpose(X)
    Y = np.transpose(Y)
    df = pd.DataFrame({'X': X, 'Y': Y})
    df = df.drop_duplicates()
    df['geometry'] = df.apply(lambda row: Point(row.X, row.Y), axis=1)
    poly = Polygon([(p.x, p.y)  for p in  df.geometry])
    return poly


def download(des_loc,
            http_page,
            str1,
            str2):
    """
    @ author:                  Shervan Gharari
    @ Github:                  https://github.com/ShervanGharari/shapefile_standardization
    @ author's email id:       sh.gharari@gmail.com
    @license:                  MIT

    This function gets name of a http and two str in the name of the link and save them in
    provided destnation
    

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
        # if download successful the statuse code is 200 then save the file, else print not downloaded
        if r.status_code == 200:
            print('download was successful for '+url)
            with open(des_loc+name, 'wb') as f:
                f.write(r.content)
        else:
            print('download was not successful for '+url)


def shp_hill (name_of_source_file, name_of_cat_file, name_of_result_file, epsilon):
    """
    @ author:                  Shervan Gharari
    @ Github:                  https://github.com/ShervanGharari/shapefile_standardization
    @ author's email id:       sh.gharari@gmail.com
    @license:                  MIT

    This function gets name of a shapefile and remove inernal holes

    Arguments
    ---------
    name_of_source_file: string, the name of the source file including path and extension
    name_of_cat_file: string, the name of the corresponding catchment (subbasin)
        for the unresolved hills
    name_of_result_file: string, the name of the file that includes fixed shapes
        including path and extension
    epsilon
    

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

    ## STEP3, break the touching polygons into separate polygons, remove the links (lines)
    shp_temp = shp_temp.buffer(-epsilon).buffer(epsilon)
    shp_temp.to_file('temp4.shp')

    ## STEP4, break the polygones into separete shape in a shapefile
    shp = gpd.read_file('temp4.shp')

    shp_all = None

    for index, _ in shp.iterrows():

        polys = shp.geometry.iloc[index] # get the shape

        if polys.type is 'Polygon':
            shp_temp = gpd.GeoSeries(polys) # convert multipolygon to a shapefile with polygons only
            shp_temp = gpd.GeoDataFrame(shp_temp) # convert multipolygon to a shapefile with polygons
            shp_temp.columns = ['geometry'] # naming geometry column
        if polys.type is 'MultiPolygon':
            shp_temp = gpd.GeoDataFrame(polys) # convert multipolygon to a shapefile with polygons 
            shp_temp.columns = ['geometry'] # naming geometry column

        if shp_all is None:
            shp_all = shp_temp
        else:
            shp_all = shp_all.append(shp_temp)

    for index, _ in shp_all.iterrows(): # assuming the code convert everything to polygone (and not multi)
        poly = shp_all.geometry.iloc[index]
        poly = remove_dublicate_point (poly)
        shp_all.geometry.iloc[index] = poly

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


def shp_std_light(name_of_source_file,
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
    name_of_result_file_fixed_shapes: string, the name of the file that includes fixed shapes
        including path and extension
    name_of_log_file: string, the name of the text log file with path and txt extension
    ID_field: string, the name of the field in the original shapefile that is used for keeping
        track of holes
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
    shp = gpd.read_file(name_of_source_file)
    print(shp.shape[0])
    shp_new = shp # pass the shape to a new shape
    shp_new['flag'] = 0 # add flag for the shapefile ids that are resolved
    
    for ID in list_id:
        for index, _ in shp.iterrows():
            if shp[ID_field][index] == ID:
                shp_temp = shp.geometry.iloc[index]
                shp_temp = shp_temp.buffer(epsilon) # to amalgamate tmultipolygons into a polygon
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
                poly = shp_new.geometry.iloc[index]
                poly = remove_dublicate_point (poly)
                shp_new.geometry.iloc[index] = poly
    
    shp_new.to_file(name_of_result_file)
    shp_new = shp_new [shp_new.flag ==1]
    if not shp_new.empty:
        shp_new.to_file(name_of_result_file_fixed_shapes)
    
#     shp_new = shp_new [shp_new.flag ==1] # get the shapes that flag are 1
#     if not shp_new.empty:
#         shp_new = shp_new.drop(columns=['flag'])
#         shp_diff = gpd.overlay(shp, shp_new, how='difference') # get the difference
#         shp_all = shp_new.append(shp_diff) # append the fixed shapefiles to the diff
#         if shp.shape[0] == shp_all.shape[0]:
#             shp_new.to_file(name_of_result_file_fixed_shapes) #saved the fixed shapefile
#             shp_all.to_file(name_of_result_file) # save the entire
#         else:
#             print('input output have different lenght; check')

def shp_std_hard(name_of_source_file,
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
    name_of_result_file_holes: string, the name of the file that includes holes including path
        and extension
    name_of_log_file: string, the name of the text log file with path and txt extension
    ID_field: string, the name of the field in the original shapefile that is used for keeping
        track of holes
    area_tolerance: float; the tolerance to compare area before and after correction and report
        differences

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
            shp_temp = gpd.GeoDataFrame(shp_temp) # convert multipolygon to a shapefile with polygons
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
                shp_temp['geometry'].iloc[index1] = shapely.geometry.polygon.orient(poly, sign = +1) 
                # +1 CCW
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
        # check if the geometry #is invalid
        if shp_poly.geometry.iloc[index].is_valid is True and invalid is True: 
            str_temp = " and becomes valid \n"
            logfile.write(str_temp)
            number_resolved = number_resolved + 1
        # check if the geometry is invalid
        if shp_poly.geometry.iloc[index].is_valid is False and invalid is True:
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


def intersection_shp(shp_1, shp_2):
    """
    @ author:                  Shervan Gharari
    @ Github:                  https://github.com/ShervanGharari/candex
    @ author's email id:       sh.gharari@gmail.com
    @license:                  Apache2

    This fucntion intersect two shapefile. It keeps the fiels from the first and second shapefiles (identified by S_1_ and 
    S_2_). It also creats other field including AS1 (area of the shape element from shapefile 1), IDS1 (an arbitary index
    for the shapefile 1), AS2 (area of the shape element from shapefile 1), IDS2 (an arbitary index for the shapefile 1), 
    AINT (the area of teh intersected shapes), AP1 (the area of the intersected shape to the shapes from shapefile 1),
    AP2 (the area of teh intersected shape to the shapefes from shapefile 2), AP1N (the area normalized in the case AP1
    summation is not 1 for a given shape from shapefile 1, this will help to preseve mass if part of the shapefile are not 
    intersected), AP2N (the area normalized in the case AP2 summation is not 1 for a given shape from shapefile 2, this
    will help to preseve mass if part of the shapefile are not intersected)
    
    Arguments
    ---------
    shp1: geo data frame, shapefile 1
    shp2: geo data frame, shapefile 2
    
    Returns
    -------
    result: a geo data frame that includes the intersected shapefile and area, percent and normalized percent of each shape
    elements in another one
    """
    # Calculating the area of every shapefile (both should be in degree or meters)
    column_names = shp_1.columns
    column_names = list(column_names)

    # removing the geometry from the column names
    column_names.remove('geometry')

    # renaming the column with S_1
    for i in range(len(column_names)):
        shp_1 = shp_1.rename(
            columns={column_names[i]: 'S_1_' + column_names[i]})

    column_names = shp_2.columns
    column_names = list(column_names)

    # removing the geometry from the colomn names
    column_names.remove('geometry')

    # renaming the column with S_2
    for i in range(len(column_names)):
        shp_2 = shp_2.rename(
            columns={column_names[i]: 'S_2_' + column_names[i]})

    # Caclulating the area for shp1
    #for index, _ in shp_1.iterrows():
    #    shp_1.loc[index, 'AS1'] = shp_1.area[index]
    #    shp_1.loc[index, 'IDS1'] = index + 1.00
    # alternative
    shp_1["AS1"] = shp_1['geometry'].area
    shp_1["IDS1"] = np.arange(1,shp_1.shape[0]+1.00)
        
    # Caclulating the area for shp2
    #for index, _ in shp_2.iterrows():
    #    shp_2.loc[index, 'AS2'] = shp_2.area[index]
    #    shp_2.loc[index, 'IDS2'] = index + 1.00
    # alternative
    shp_2["AS2"] = shp_2['geometry'].area
    shp_2["IDS2"] = np.arange(1,shp_2.shape[0]+1.00)
        
    # making intesection
    result = spatial_overlays (shp_1, shp_2, how='intersection')
    # result = geopandas.tools.overlay(shp_1, shp_2, how='intersection')
    # result = geopandas.overlay(shp_1, shp_2, how='intersection')

    # Caclulating the area for shp2
    result['AINT'] = result['geometry'].area
    result['AP1'] = result['AINT']/result['AS1']
    result['AP2'] = result['AINT']/result['AS2']
    
    
    # taking the part of data frame as the numpy to incread the spead
    # finding the IDs from shapefile one
    ID_S1 = np.array (result['IDS1'])
    AP1 = np.array(result['AP1'])
    AP1N = AP1 # creating the nnormalized percent area
    ID_S1_unique = np.unique(ID_S1) #unique idea
    for i in ID_S1_unique:
        INDX = np.where(ID_S1==i) # getting the indeces
        AP1N[INDX] = AP1[INDX] / AP1[INDX].sum() # normalizing for that sum
        
    # taking the part of data frame as the numpy to incread the spead
    # finding the IDs from shapefile one
    ID_S2 = np.array (result['IDS2'])
    AP2 = np.array(result['AP2'])
    AP2N = AP2 # creating the nnormalized percent area
    ID_S2_unique = np.unique(ID_S2) #unique idea
    for i in ID_S2_unique:
        INDX = np.where(ID_S2==i) # getting the indeces
        AP2N[INDX] = AP2[INDX] / AP2[INDX].sum() # normalizing for that sum
        
    result ['AP1N'] = AP1N
    result ['AP2N'] = AP2N
    
def spatial_overlays(df1, df2, how='intersection', reproject=True):
    """Perform spatial overlay between two polygons.

    Currently only supports data GeoDataFrames with polygons.
    Implements several methods that are all effectively subsets of
    the union.
    
    Ömer Özak
    ozak
    https://github.com/ozak
    https://github.com/geopandas/geopandas/pull/338

    Parameters
    ----------
    df1 : GeoDataFrame with MultiPolygon or Polygon geometry column
    df2 : GeoDataFrame with MultiPolygon or Polygon geometry column
    how : string
        Method of spatial overlay: 'intersection', 'union',
        'identity', 'symmetric_difference' or 'difference'.
    use_sindex : boolean, default True
        Use the spatial index to speed up operation if available.

    Returns
    -------
    df : GeoDataFrame
        GeoDataFrame with new set of polygons and attributes
        resulting from the overlay

    """
    df1 = df1.copy()
    df2 = df2.copy()
    df1['geometry'] = df1.geometry.buffer(0)
    df2['geometry'] = df2.geometry.buffer(0)
    if df1.crs!=df2.crs and reproject:
        print('Data has different projections.')
        print('Converted data to projection of first GeoPandas DatFrame')
        df2.to_crs(crs=df1.crs, inplace=True)
    if how=='intersection':
        # Spatial Index to create intersections
        spatial_index = df2.sindex
        df1['bbox'] = df1.geometry.apply(lambda x: x.bounds)
        df1['sidx']=df1.bbox.apply(lambda x:list(spatial_index.intersection(x)))
        pairs = df1['sidx'].to_dict()
        nei = []
        for i,j in pairs.items():
            for k in j:
                nei.append([i,k])
        pairs = gpd.GeoDataFrame(nei, columns=['idx1','idx2'], crs=df1.crs)
        pairs = pairs.merge(df1, left_on='idx1', right_index=True)
        pairs = pairs.merge(df2, left_on='idx2', right_index=True, suffixes=['_1','_2'])
        pairs['Intersection'] = pairs.apply(lambda x: (x['geometry_1'].intersection(x['geometry_2'])).buffer(0), axis=1)
        pairs = gpd.GeoDataFrame(pairs, columns=pairs.columns, crs=df1.crs)
        cols = pairs.columns.tolist()
        cols.remove('geometry_1')
        cols.remove('geometry_2')
        cols.remove('sidx')
        cols.remove('bbox')
        cols.remove('Intersection')
        dfinter = pairs[cols+['Intersection']].copy()
        dfinter.rename(columns={'Intersection':'geometry'}, inplace=True)
        dfinter = gpd.GeoDataFrame(dfinter, columns=dfinter.columns, crs=pairs.crs)
        dfinter = dfinter.loc[dfinter.geometry.is_empty==False]
        dfinter.drop(['idx1','idx2'], inplace=True, axis=1)
        return dfinter
    elif how=='difference':
        spatial_index = df2.sindex
        df1['bbox'] = df1.geometry.apply(lambda x: x.bounds)
        df1['sidx']=df1.bbox.apply(lambda x:list(spatial_index.intersection(x)))
        df1['new_g'] = df1.apply(lambda x: reduce(lambda x, y: x.difference(y).buffer(0), 
                                 [x.geometry]+list(df2.iloc[x.sidx].geometry)) , axis=1)
        df1.geometry = df1.new_g
        df1 = df1.loc[df1.geometry.is_empty==False].copy()
        df1.drop(['bbox', 'sidx', 'new_g'], axis=1, inplace=True)
        return df1
    elif how=='symmetric_difference':
        df1['idx1'] = df1.index.tolist()
        df2['idx2'] = df2.index.tolist()
        df1['idx2'] = np.nan
        df2['idx1'] = np.nan
        dfsym = df1.merge(df2, on=['idx1','idx2'], how='outer', suffixes=['_1','_2'])
        dfsym['geometry'] = dfsym.geometry_1
        dfsym.loc[dfsym.geometry_2.isnull()==False, 'geometry'] = dfsym.loc[dfsym.geometry_2.isnull()==False, 'geometry_2']
        dfsym.drop(['geometry_1', 'geometry_2'], axis=1, inplace=True)
        dfsym = gpd.GeoDataFrame(dfsym, columns=dfsym.columns, crs=df1.crs)
        spatial_index = dfsym.sindex
        dfsym['bbox'] = dfsym.geometry.apply(lambda x: x.bounds)
        dfsym['sidx'] = dfsym.bbox.apply(lambda x:list(spatial_index.intersection(x)))
        dfsym['idx'] = dfsym.index.values
        dfsym.apply(lambda x: x.sidx.remove(x.idx), axis=1)
        dfsym['new_g'] = dfsym.apply(lambda x: reduce(lambda x, y: x.difference(y).buffer(0), 
                         [x.geometry]+list(dfsym.iloc[x.sidx].geometry)) , axis=1)
        dfsym.geometry = dfsym.new_g
        dfsym = dfsym.loc[dfsym.geometry.is_empty==False].copy()
        dfsym.drop(['bbox', 'sidx', 'idx', 'idx1','idx2', 'new_g'], axis=1, inplace=True)
        return dfsym
    elif how=='union':
        dfinter = spatial_overlays(df1, df2, how='intersection')
        dfsym = spatial_overlays(df1, df2, how='symmetric_difference')
        dfunion = dfinter.append(dfsym)
        dfunion.reset_index(inplace=True, drop=True)
        return dfunion
    elif how=='identity':
        dfunion = spatial_overlays(df1, df2, how='union')
        cols1 = df1.columns.tolist()
        cols2 = df2.columns.tolist()
        cols1.remove('geometry')
        cols2.remove('geometry')
        cols2 = set(cols2).intersection(set(cols1))
        cols1 = list(set(cols1).difference(set(cols2)))
        cols2 = [col+'_1' for col in cols2]
        dfunion = dfunion[(dfunion[cols1+cols2].isnull()==False).values]
        return dfunion

