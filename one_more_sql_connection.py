import datetime
import mysql.connector as con

__cnx = None

def get_sql_connection():
  print("Opening mysql connection")
  global __cnx

  if __cnx is None:
    __cnx = con.connect(user='root', password='shadowdrive2003', database='exam1')

  return __cnx