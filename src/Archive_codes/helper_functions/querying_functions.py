import psycopg2
from psycopg2 import sql
from helper_functions.sql_connect_functions import connect
from bash_commands import list_layers

import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, parent_dir)

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


def tables_with_invalid_geom(file_name: str, year: int):
     """
     Find layers with invalid geometries and return them
     """
     conn = connect()
     if conn is None:
          return
     
     layer_names = list_layers(file_name, year)
     result = []
     
     for layer in layer_names:
          table_name = str(year) + "_" + layer
          query = sql.SQL("""
          SELECT id
          FROM {table}
          WHERE NOT ST_IsValid(geom);
          """).format(
               table = sql.Identifier(table_name)
          )
          try:
               with conn:
                    with conn.cursor() as cur:
                         cur.execute(query)
                         if cur.description:
                              rows = cur.fetchall()
                              # only record layers that have invalid geoms
                              if rows:
                                   result.append(layer)
                              else:
                                   print("No invalid tables present")
          
          except(Exception, psycopg2.DatabaseError) as error:
               print("Query error:", error)
     
     conn.close()
     return result



def repair_layer(filename: str, year: int):
     """
     repair geospatial layers that are found to have invalid geometries
     """
     conn = connect()
     if conn is None:
          return

     # check for tables to repair
     tables_to_repair = tables_with_invalid_geom(filename, year)

     for table in tables_to_repair:
          table_name = str(year) + "_" + table
          query = sql.SQL("""
          UPDATE {table}
          SET geom = ST_CollectionExtract(ST_MakeValid(geom), 3)::geometry(MultiPolygon, 3414)
          WHERE NOT ST_IsValid(geom);
          """).format(
               table = sql.Identifier(table_name)
          )
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


def construct_union_query(table_name: str, output_table_name: str):
     """
     returns query to union layer with the hectare grid table
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


def union_with_hectare(filename: str, year: int):
     """
     Unions the layers with the singapore hectare grid
     """
     layers = list_layers(filename, year)

     queries = []

     # construct the query to be ran
     for layer in layers:
          output_table_name = str(year) + "_" + layer + "_grid"
          table_name = str(year) + "_" + layer
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


def combine_tables(filename: str, year: int, map_draw_order: dict):
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
     layers = list_layers(filename, year)
     output_table_name = f"{year}_COMBINED_grid"

     # collect union of all column names
     all_columns = set()
     layer_columns = {}
     for layer in layers:
          table_name = f"{year}_{layer}_grid"
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


# ogr2ogr -f GPKG singapore_2018_with_hectare.gpkg \
# PG:"dbname=postgis user=yitong" \
# -sql "SELECT *, ST_Area(geom)/10000.0 AS hectares 
#       FROM \"2018_COMBINED_grid\"
#       ORDER BY draw_order"
