# shapefile_standardization
Fix invalid shapes in a shapefile to make them ready for GIS manipulation

The scripts fix invalid or self-intersecting shapefiles, provide a statistics on the number of shapefiles that are invalid and became validated and also the shapefiles that have holes.

The holes, if present, are taken out and saved as a separaete shapefile which can be used to take them out from the shapes if needed.

## Specification of task for correcting MERIT_Hydro bug fixed

The code shp_std_def.py can be used to correct the shapefile. It loops over the shape of a shapefile, decompose the shape into polygons and then merge them. if there is a signle hole in the shape it take it out and save it as a separat shapefile.

There were two occations for COMID of XXX and XXX that were fixed manually. Still after applying the correction to the shapefile and based on the check geometry there are handful of shapes that are not validated. Those shapes are manually validated and put back into the shapefiles. The corrected shapefiles are check on more time in QGIS for validity of their shapes. As an example, in the manually corrected shapefiles so far from North America COMID of XXX are manually fixed.

The manually fixed shapefiles are intersected with the ERA-5 shapefile based on candex. The relevant fields are:

"COMID"    # COMID (hruId) that is used for SUMMA
"lat"      # lat of hru
"lon"      # lon of hru
"ERA5ID"   # ERA5 grid ID, not used
"ERA5lat"  # lat of forcing grid to be read
"ERA5lon"  # lon of forcing grid to be read
"ERA5W"    # weight of each ERA5 grid in subbasin


