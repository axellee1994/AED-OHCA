import subprocess
import os
import sys
import re

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, parent_dir)

from helper_functions.delimiters import split_command

# Point to the proj.db inside the active environment
# found using: "find /Users/yitong/opt/anaconda3/ -name proj.db"
# Due to conflicting GDAL installs in Homebrew and conda, VScode is pointing to the Homebrew install
# This points it to use the conda installed GDAL.
os.environ["PATH"] = "/Users/yitong/opt/anaconda3/envs/geopandasNew/bin:" + os.environ["PATH"]
os.environ["PROJ_LIB"] = "/Users/yitong/opt/anaconda3/envs/geopandasNew/share/proj"
os.environ["GDAL_DATA"] = "/Users/yitong/opt/anaconda3/envs/geopandasNew/share/gdal"


def convert_to_SVY21(output, input, year):
    """
    Converts gpkg file from EPSG 4326 to EPSG 3414 (SVY21, Singapore, units in metres).
    So as to set hectare grids accurately. 
    """
    cmd = [
        "ogr2ogr", "-f", "GPKG", output, input, "-t_srs", "EPSG:3414"
    ]

    result = subprocess.run(cmd, capture_output=True,
                            text=True, cwd = parent_dir + "/datasets/geospatial_data/"+ str(year) +"_geospatial/")
    print("Done")
    # print("stdout:", result.stdout)
    # print("stderr:", result.stderr)

def list_layers(input, year):
    """
    returns the layers in a gpkg file
    does not include the "other_relations" layer as it does not include 
    """
    cmd = [
        "ogrinfo", input, "-so"
    ]
    result = subprocess.run(cmd, capture_output=True,
                            text=True, cwd = parent_dir + "/datasets/geospatial_data/"+ str(year) +"_geospatial/")
    
    # retrieve the layer names using regex
    layer_names = re.findall(r'^\d+:\s+([^\(\s]+)', result.stdout, re.MULTILINE)
    # remove "other_relations" as it does not have geom column
    if "other_relations" in layer_names:
        layer_names.remove("other_relations")
    return layer_names


def add_to_postgres(input: str, year: int):
    """
    adds the layers from .gpkg file to postgreSQL
    Can't get PostgreSQL command to work,
    need to manually copy command output and run in terminal
    """
    layer_names = list_layers(input, year)
    for layer_name in layer_names:
        # cmd = [
        #     'ogr2ogr', '-f', 'PostgreSQL', 
        #     'PG:"dbname=postgis user=yitong"', 
        #     input, '-nln', str(year)+ "_" +layer_name, '-lco', 
        #     'GEOMETRY_NAME=geom', '-lco', 'FID=id', 
        #     '-nlt', 'PROMOTE_TO_MULTI', layer_name
        # ]
        cmd = "ogr2ogr -f PostgreSQL PG:\"dbname=postgis user=yitong\" " + input + " -nln " + str(year)+ "_" +layer_name + " -lco GEOMETRY_NAME=geom -lco FID=id -nlt PROMOTE_TO_MULTI " + layer_name
        print(cmd)
        # result = subprocess.run(cmd, capture_output=True,
        #         text=True, cwd = os.path.join(parent_dir + "/datasets/geospatial_data/"+ str(year) +"_geospatial/")
        # )
        # print("stdout:", result.stdout)
        # print("stderr:", result.stderr)

    
    print("Done")

# convert_to_SVY21("singapore_2020_3414.gpkg", "singapore_2020.gpkg", 2020)
# print(list_layers("singapore_2020_3414.gpkg", 2020))
# add_to_postgres("singapore_2020_3414.gpkg", 2020)
