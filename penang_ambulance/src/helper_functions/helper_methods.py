import psycopg2
from psycopg2 import sql
import subprocess
import re
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, parent_dir)

from src.helper_functions.sql_connection_functions import connect

# print(parent_dir)

def list_layers(input):
    """
    returns the layers in a gpkg file
    does not include the "other_relations" layer as it does not include 
    """
    cmd = [
        "ogrinfo", input, "-so"
    ]
    result = subprocess.run(cmd, capture_output=True,
                            text=True, cwd = parent_dir + "/datasets/penang_maps/")
    
    # retrieve the layer names using regex
    layer_names = re.findall(r'^\d+:\s+([^\(\s]+)', result.stdout, re.MULTILINE)
    # remove "other_relations" as it does not have geom column
    if "other_relations" in layer_names:
        layer_names.remove("other_relations")
    # remove points and multilinestrings as they are not needed
    if "points" in layer_names:
        layer_names.remove("points")
    if "multilinestrings" in layer_names:
        layer_names.remove("multilinestrings")

    return layer_names

def query_column_names(params = None):
     """
     Provide name of the SQL table
     input example: query_column_names("2020_multipolygons",)
     returns a list of all the column names in the table
     """
     conn = connect()
     if conn is None:
          return
     sql = """
     SELECT column_name
     FROM INFORMATION_SCHEMA.COLUMNS
     WHERE TABLE_NAME = %s;
     """
     try:
          with conn:
               with conn.cursor() as cur:
                    cur.execute(sql, (params,) if isinstance(params, str) else params)
                    if cur.description: # if query returns rows
                         rows = cur.fetchall()
                         # return as a list instead of a tuple
                         return [r[0] for r in rows]
                    
     except(Exception, psycopg2.DatabaseError) as error:
          print("Query error:", error)
     finally:
          conn.close()


def query_distinct_values(column_name: str, table_name: str):
     """
     returns a list of unique values of a column

     Parameters
     ------
     column_name: str
          name of column you want to query

     table_name: str
          name of the table you want to query
     """

     conn = connect()
     if conn is None:
          return
     query = "SELECT DISTINCT " + f"\"{column_name}\"" + " FROM " + f"\"{table_name}\"" + ";"
     try:
          with conn:
               with conn.cursor() as cur:
                    cur.execute(query)
                    if cur.description:
                         rows = cur.fetchall()
                         return([r[0] for r in rows])
     except(Exception, psycopg2.DatabaseError) as error:
          print("Query error:", error)


def construct_union_query(table_name: str, output_table_name: str):
     """
     returns query to union layer with the hectare grid table

     Parameters
     ------
     table_name : str
          name of the table you want to query
     output_table_name : str
          name of the output table you want to create. 
     """
     column_names = query_column_names(table_name)
     # print(column_names)
     if "geom" in column_names:
          column_names.remove("geom")

     query_parts = []
     query_parts.append("DROP TABLE IF EXISTS \"{output_table_name}\";")
     query_parts.append("CREATE TABLE \"{output_table_name}\" AS")
     query_parts.append("SELECT g.id AS grid_id, ")
     
     for name in column_names:
          query_parts.append("l." + name + " AS " + name + ", ")

     query_parts.append("""ST_Intersection(ST_MakeValid(l.geom), g.geom) AS geom 
                  FROM hectare_grids g
                  JOIN \"{table_name}\" l
                  ON ST_Intersects(g.geom, l.geom);""")

     query = "\n".join(query_parts)
     query = query.format(
          table_name = table_name,
          output_table_name = output_table_name
     )

     return query


def union_with_hectare(filename: str):
     """
     Unions the layers with the singapore hectare grid
     """
     layers = list_layers(filename)

     queries = []

     # construct the query to be ran
     for layer in layers:
          output_table_name = "penang" + "_" + layer + "_grid"
          table_name = "penang" + "_" + layer
          queries.append(construct_union_query(table_name, output_table_name))
     
     conn = connect()
     if conn is None:
          return
     for query in queries:
          try:
               with conn:
                    with conn.cursor() as cur:
                         cur.execute(query)
                         if cur.description:
                              rows = cur.fetchall()
                              print([r[0] for r in rows])
          except(Exception, psycopg2.DatabaseError) as error:
               print("Query error:", error)
          
     conn.close()

def combine_tables(filename: str, map_draw_order: dict):
     """
     To "stack" however many sql tables together
     column names for each table will need to be listed in the same order
     For column names that are not in a table, "NULL AS" will need to be added in front.
     Can't get PostgreSQL command to work,
     need to manually copy command output and run in terminal

     Parameters
     ------
     filename : str
          Input file name
     year : int
          Year of the dataset
     draw_order_map : dict
          Mapping of geom_type -> draw_order
          Example: {"multipolygons": 1, "lines": 2, "multilinestrings": 2, "points": 3}
     """
     layers = list_layers(filename)
     
     output_table_name = f"penang_COMBINED_grid"

     # collect union of all column names
     all_columns = set()
     layer_columns = {}
     for layer in layers:
          table_name = f"penang_{layer}_grid"
          col_names = query_column_names(table_name)
          layer_columns[table_name] = col_names
          # add to the set of column names
          all_columns.update(col_names)
     
     # force a consistent order 
     all_columns = list(sorted(all_columns))

     queries = []
     # construct the query's SELECT portion
     for table_name, col_names in layer_columns.items():
          partial_query = []
          for col in all_columns:
               if col in col_names:
                    # if column name is found in the table
                    partial_query.append(f"\"{col}\"")
               else:
                    # if column name is not found in the table
                    # add NULL AS in front of the column name
                    partial_query.append(f"NULL AS \"{col}\"")
          partial_query.append(f"\'{table_name}\' AS src")
          # obtain layer name from the table_name eg: 2019_multipolygons_grid
          geom_type = table_name[5:-5]
          partial_query.append(f"\'{geom_type}\' AS geom_type")

          # lookup draw_order from provided dictionary (default 99 if missing)
          draw_order = map_draw_order.get(geom_type, 99)
          partial_query.append(f"{draw_order} AS draw_order")


          query = f'SELECT {", ".join(partial_query)} FROM "{table_name}"'
          queries.append(query)

     drop_query = f"DROP TABLE IF EXISTS \"{output_table_name}\";\n"
     create_table = f"CREATE TABLE \"{output_table_name}\" AS\n"

     # Join with UNION ALL
     # .join adds UNION ALL in between the list of queries
     full_query = drop_query + create_table + "\nUNION ALL\n".join(queries) + ";"
     print(full_query)