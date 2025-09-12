"""
main function that executes sql queries
"""
import os
import sys
# parent_dir points at src folder (because of the '..')
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from helper_functions.querying_functions import query_column_names, tables_with_invalid_geom, repair_layer, union_with_hectare

if __name__ == '__main__':

    ## get the column names of a table
    # column_names = query_column_names("2020_multipolygons",)
    # if column_names:
    #      print(column_names)

    ## get tables that contain invalid geometries 
    # containing_invalid_geoms = tables_with_invalid_geom("singapore_2020_3414.gpkg", 2020)
    # containing_invalid_geoms and print(containing_invalid_geoms)

    # repair the tables that contain invalid geometries
    # repair_layer("singapore_2020_3414.gpkg", 2020)

    union_with_hectare("singapore_2020_3414.gpkg", 2020)

