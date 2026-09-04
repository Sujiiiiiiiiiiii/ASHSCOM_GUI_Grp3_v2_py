import mysql.connector
from mysql.connector import Error

def create_connection():
    connection = None

    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='root',
            database='ASHCOMManagement'
        )
        return connection
    except Error as e:
        pass

    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='roots',
            database='ASHCOMManagement'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")

    return connection

if __name__ == "__main__":
    conn = create_connection()
    if conn and conn.is_connected():
        print("Database connected successfully!")
        conn.close()