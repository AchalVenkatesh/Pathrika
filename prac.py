from database import updated
from sql_connection import get_sql_connection

connection = get_sql_connection()

updated(connection, "m1","Vasudeva")

