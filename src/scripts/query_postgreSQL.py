"""
main function that executes sql queries
"""
import os
import sys
# parent_dir points at src folder (because of the '..')
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from bash_commands import convert_to_SVY21, add_to_postgres
from helper_functions.querying_functions import query_column_names, tables_with_invalid_geom, repair_layer, union_with_hectare, combine_tables

if __name__ == '__main__':

    # convert .gpkg from EPSG 4326 to EPSG 3414 (SVY21, Singapore, units in metres).
    # convert_to_SVY21("singapore_2018_3414.gpkg", "singapore_2018.gpkg", 2018)

    # add_to_postgres("singapore_2018_3414.gpkg", 2018)

    ## get the column names of a table
    # column_names = query_column_names("2020_multipolygons",)
    # if column_names:
    #      print(column_names)

    ## get tables that contain invalid geometries 
    # containing_invalid_geoms = tables_with_invalid_geom("singapore_2018_3414.gpkg", 2018)
    # containing_invalid_geoms and print(containing_invalid_geoms)

    ## repair the tables that contain invalid geometries
    # repair_layer("singapore_2018_3414.gpkg", 2018)

    # union_with_hectare("singapore_2018_3414.gpkg", 2018)

# ordering the layer so that multipolygons layer does not cover the other layers
    map_draw_order = {
        "multipolygons": 1,
        "lines": 2,
        "multilinestrings": 2,
        "points": 3
    }
    combine_tables("singapore_2020_3414.gpkg", 2020, map_draw_order)


