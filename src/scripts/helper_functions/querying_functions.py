import psycopg2
from psycopg2 import sql
from helper_functions.sql_connect_functions import connect
from bash_commands import list_layers

# import os
# import sys
# parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
# sys.path.insert(0, parent_dir)

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


def tables_with_invalid_geom(file_name, year):
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
          
          except(Exception, psycopg2.DatabaseError) as error:
               print("Query error:", error)
     
     conn.close()
     return result



def repair_layer(filename, year):
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


def construct_union_query(table_name, output_table_name):
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
     # print(query_parts)
     query = "\n".join(query_parts)
     query = query.format(
          table_name = table_name,
          output_table_name = output_table_name
     )

     return query


def union_with_hectare(input, year):
     """
     Unions the layers with the singapore hectare grid
     """
     layers = list_layers(input, year)

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
                              rows = cur.fetchal()
                              print([r[0] for r in rows])
          except(Exception, psycopg2.DatabaseError) as error:
               print("Query error:", error)
          
     conn.close()

SELECT grid_id, id, osm_id, name, highway, waterway, aerialway, barrier, man_made, z_order, other_tags, NULL, geom AS src
FROM "2019_lines_grid"
UNION ALL
SELECT grid_id, id, osm_id, name, NULL AS highway, NULL AS waterway, NULL AS aerialway, NULL AS barrier, NULL AS man_made, NULL AS z_order, other_tags, type, geom AS src
FROM "2019_multilinestrings_grid";


def combine_tables(tables: list[str]):
     """
     To "stack" however many sql tables together
     """
     