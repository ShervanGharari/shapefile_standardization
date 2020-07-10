# shapefile_standardization
Fix invalid shapes in a shapefile to make them ready for GIS manipulation

The scripts fix invalid or selfintersecting shapefiles, provide a statistics on the number of shapefiles that are invalid and became validated and also the shapefiles that have holes.

The holes, if present, are taken out and saved as a separaete shapefile which can be used to explode their areas from the polygones is needed. 
