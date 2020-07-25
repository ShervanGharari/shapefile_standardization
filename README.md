# shapefile_standardization
Fix invalid shapes in a shapefile to make them ready for GIS manipulation

The scripts fix invalid or self-intersecting shapefiles, provide a statistics on the number of shapefiles that are invalid and became validated and also the shapefiles that have holes.

The holes, if present, are taken out and saved as a separaete shapefile which can be used to take them out from the shapes if needed.


### Note

The shapefiles are corrected for the North America domain can become invalid if they undergo any changes, intersection, etc, depending on the program used. It is always best to check them after any manupulaion in case valid resulting shapefiles are needed.

