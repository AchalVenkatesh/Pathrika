from datetime import datetime
from sql_connection import get_sql_connection
import mysql.connector
import time

def tounix(date):
    date_obj = datetime.strptime(date, '%Y-%m-%dT%H:%M')
    return int(date_obj.timestamp())

def insert_user(connection, user_id, role, password):
    try:
        query = "INSERT INTO users (user_id, role, password) VALUES (%s,%s,%s);"
        cur = connection.cursor(buffered=True)
        cur.execute(query, (user_id, role, password))
        connection.commit()
        cur.close()
    except mysql.connector.Error as e:
        print(f"Error inserting user: {e}")
        try:
            connection.rollback()
        except:
            pass
    
def insert_request(connection, exam_id, release_date, teacher_id):
    try:
        query = "INSERT INTO requests (exam_id, release_date, user_id,update_status) VALUES (%s,%s,%s,0);"
        cur = connection.cursor(buffered=True)
        cur.execute(query, (exam_id, release_date, teacher_id))
        connection.commit()
        cur.close()
    except mysql.connector.Error as e:
        print(f"Error inserting request: {e}")
        try:
            connection.rollback()
        except:
            pass

def fetch_request(connection, user_id):
    cur = connection.cursor(buffered=True)
    
    try:
        query = "SELECT exam_id FROM requests WHERE user_id = %s AND update_status = 0"
        cur.execute(query, (user_id,))
        response = [row[0] for row in cur.fetchall()]  # Fetch all results
        return response
    except mysql.connector.Error as e:
        print(f"Error fetching requests: {e}")
        return []  # Return an empty list on error
    finally:
        cur.close()  # Ensure the cursor is closed

def fetch_exams(connection):
    cur = connection.cursor(buffered=True)
    
    try:
        query = "SELECT exam_id FROM exams"
        cur.execute(query)
        response = [row[0] for row in cur.fetchall()]  # Fetch all results
        return response
    except mysql.connector.Error as e:
        print(f"Error fetching exams: {e}")
        return []  # Return an empty list on error
    finally:
        cur.close()  # Ensure the cursor is closed

def fetch_alerts(connection):
    cur = connection.cursor(buffered=True)
    
    try:
        query = "SELECT * FROM alerts"
        cur.execute(query)
        columns = [column[0] for column in cur.description]  # Get column names
        response = [dict(zip(columns, row)) for row in cur.fetchall()]  # Create a list of dictionaries
        return response
    except mysql.connector.Error as e:
        print(f"Error fetching exams: {e}")
        return []  # Return an empty list on error
    finally:
        cur.close()
 
    
def fetch_teacher(connection, exam_id):
    cur = connection.cursor(buffered=True)
    
    try:
        query = "SELECT user_id FROM requests WHERE exam_id = %s"
        cur.execute(query, (exam_id,))
        response = [row[0] for row in cur.fetchall()]  # Fetch all results
        return response
    except mysql.connector.Error as e:
        print(f"Error fetching teachers: {e}")
        return []  # Return an empty list on error
    finally:
        cur.close()  # Ensure the cursor is closed

def is_valid(connection, user_id, role, password):
    cur = connection.cursor(buffered=True)
    
    try:
        query = "SELECT user_id FROM users WHERE user_id=%s AND role=%s AND password=%s;"
        cur.execute(query, (user_id, role, password))
        
        response = cur.fetchone()
        
        return response is not None
    except mysql.connector.Error as e:
        print(f"Error validating user: {e}")
        return False
    finally:
        cur.close()

def delete_request(connection, exam_id, user_id):
     try:
         query = "DELETE FROM requests WHERE exam_id=%s and user_id=%s;"
         cur = connection.cursor(buffered=True)
         cur.execute(query, (exam_id, user_id))
         connection.commit()
         print("deleted")
         cur.close()
     except mysql.connector.Error as e:
         print(f"Error deleting request: {e}")
         try:
             connection.rollback()
         except:
             pass

def get_time(connection, exam_id):
    cur = connection.cursor(buffered=True)

    try:
        query = "SELECT release_date FROM requests WHERE exam_id=%s;"
        cur.execute(query, (exam_id,))
        response = cur.fetchone()

        if response is not None:
            return int(response[0])
        else:
            raise ValueError("No results found for the given exam ID.")
    except (mysql.connector.Error, ValueError) as e:
        print(f"Error getting time: {e}")
        raise
    finally:
        cur.close()  # Ensure the cursor is closed

def updated(connection, exam_id, user_id):
    try:
        query = "UPDATE requests SET update_status = '1' WHERE exam_id = %s AND user_id = %s;"
        cur = connection.cursor(buffered=True)
        cur.execute(query, (exam_id, user_id))
        connection.commit()
        print("updated")
        cur.close()
    except mysql.connector.Error as e:
        print(f"Error updating request status: {e}")
        try:
            connection.rollback()
        except:
            pass

def reset_connection(connection):
    try:
        connection.reset_session()
    except Exception as e:
        print(f"Error resetting connection: {e}")

def add_exam(connection, subjectName, subjectCode):
    cur = connection.cursor(buffered=True)
    try:
        query = "INSERT INTO exams (subject_name, exam_id) VALUES (%s, %s)"
        cur = connection.cursor(buffered=True)
        cur.execute(query, (subjectName, subjectCode))
        connection.commit()
        cur.close()
    except mysql.connector.Error as e:
        print(f"Error inserting exam: {e}")
        try:
            connection.rollback()
        except:
            pass
    finally:
        cur.close()

def add_alert(connection, user_id, exam_id):
    cur = connection.cursor(buffered=True)
    current_time = int(time.time())
    try:
        query = "INSERT INTO alerts (user_id, exam_id, time) VALUES (%s, %s, %s)"
        cur = connection.cursor(buffered=True)
        cur.execute(query, (user_id, exam_id,current_time))
        connection.commit()
        cur.close()
    except mysql.connector.Error as e:
        print(f"Error inserting alert: {e}")
        try:
            connection.rollback()
        except:
            pass
    finally:
        cur.close()

def save_keys(connection, hashedkey, swarm_key, username):
    cur = connection.cursor(buffered=True)
    try:
        query = "UPDATE admins SET swarm_key = %s, private_key = %s, isSwarmKey = 1, isPrivateKey = 1 WHERE username = %s;"
        cur = connection.cursor(buffered=True)
        cur.execute(query, (swarm_key, hashedkey, username))
        connection.commit()
        cur.close()
    except mysql.connector.Error as e:
        print(f"Error inserting alert: {e}")
        try:
            connection.rollback()
        except:
            pass
    finally:
        cur.close()

def isPrivateKey(connection, username):
    cur = connection.cursor(buffered=True)
    
    try:
        query = "SELECT private_key FROM admins WHERE username=%s;"
        cur.execute(query, (username,))
        
        result = cur.fetchone()
        print(result)  # Debugging line to see what result is
        
        # Check if the result is None or if the private_key is empty
        if result is None or result[0] is None or result[0] == "":
            return False  # Indicates that the private key is empty
        
        return True  # Indicates that the private key exists
    except mysql.connector.Error as e:
        print(f"Error checking private key: {e}")
        return False
    finally:
        cur.close()



def is_Admin_valid(connection, username, password):
    cur = connection.cursor(buffered=True)
    
    try:
        query = "SELECT username FROM admins WHERE username=%s AND password=%s;"
        cur.execute(query, (username, password))
        
        response = cur.fetchone()
        
        return response is not None  # Returns True if admin exists, otherwise False
    except mysql.connector.Error as e:
        print(f"Error validating admin: {e}")
        return False
    finally:
        cur.close()

def joined_network(connection, username):
    cur = connection.cursor(buffered=True)
    
    try:
        query = "SELECT got_swarm_key FROM users WHERE username=%s;"
        cur.execute(query, (username,))
        
        result = cur.fetchone()
        print(result)  # Debugging line to see what result is
        
        # Check if the result is None or if the private_key is empty
        if result is None or result[0] is None or result[0] == "":
            return False  # Indicates that the private key is empty
        
        return True  # Indicates that the private key exists
    except mysql.connector.Error as e:
        print(f"Error checking if got swarm key: {e}")
        return False
    finally:
        cur.close()

# # Main execution
# connection = get_sql_connection()

# try:
#     a = get_time(connection, "e1")
#     print(a)
#     reset_connection(connection)
#     updated(connection, "e1", "t1")
# except Exception as e:
#     print(f"An error occurred: {e}")
# finally:
#     if connection.is_connected():
#         connection.close()