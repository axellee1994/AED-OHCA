"""
Connection to database
"""

import psycopg2
from configparser import ConfigParser

import os
import sys
# setting parent_dir so that file can be ran from any working directory.
# As long as the correct command is ran eg "python scripts/query_postfreSQL.py"
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, parent_dir)

def config(filename= parent_dir+"/src/database.ini", section="postgresql"):
    """
    config() function reads the database.ini file and returns connection parameters. 
    """
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]

    else:
        raise Exception("Section {0} not found in the {1} file".format(section, filename))
    return db


def connect():
    """
    connect to database base on database.ini, uses config()
    """
    conn = None
    try:
        # read connection parameters
        params = config()
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error connecting to database", error)
    
    # conn will be None if connection is not made
    # return conn to continue interacting with the database
    return conn