import psycopg2
import pandas as pd
from sqlalchemy import create_engine

host='localhost'
database='IE271Project'
user='postgres'
port=5432
password='password'

# pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection.
engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")

#### ==== #### ==== #### ==== #### ==== ####

#### ==== #### ==== CONNECTING TO THE DATABASE ==== #### ==== ####

def getdblocation():
    db = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        port=port,
        # password='password'
        password=password
    )
    return db

#### ==== #### ==== ALLOWING TO MODIFY THE DATABASE ==== #### ==== ####

def modifydatabase(sql, values):
    db = getdblocation()
    cursor = db.cursor()
    cursor.execute(sql, values)
    db.commit()
    db.close()

#### ==== #### ==== RETRIEVING DATA FROM THE DATABASE ==== #### ==== ####

def querydatafromdatabase(sql, values, dfcolumns):
    # ARGUMENTS
    # sql -- sql query with placeholders (%s)
    # values -- values for the placeholders
    # dfcolumns -- column names for the output
    db = getdblocation()
    cur = db.cursor()
    cur.execute(sql, values)
    rows = pd.DataFrame(cur.fetchall(), columns=dfcolumns)
    db.close()
    return rows