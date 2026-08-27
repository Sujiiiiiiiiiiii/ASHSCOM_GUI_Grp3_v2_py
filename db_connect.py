import mysql.connector
from mysql.connector import Error

def create_connection():
    connection = None

    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='root',
            database='ashcommanagement'
        )
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    return connection

if __name__ == "__main__":
    conn = create_connection()
    if conn and conn.is_connected():
        print("Database connected successfully!")
        conn.close()