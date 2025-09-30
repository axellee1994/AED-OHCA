import psycopg2
from psycopg2 import sql
import subprocess
import re
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, parent_dir)

from helper_methods import query_column_names, list_layers, union_with_hectare, combine_tables, construct_union_query

# print(parent_dir)

# print(query_column_names("scene_points"))
# print(list_layers("penang_3375.gpkg"))

# union_with_hectare("penang_3375.gpkg")
print(construct_union_query("scene_points", "scene_points_points"))

# ordering the layer so that multipolygons layer does not cover the other layers
# map_draw_order = {
#      "multipolygons": 1,
#      "lines": 2,
# }
# combine_tables("penang_3375.gpkg", map_draw_order)