import mysql.connector
from mysql.connector import Error
 
def check_database_connection():
    try:
        # Create a connection to the database
        connection = mysql.connector.connect(
            host='localhost',       # Change to your host
            user='root',            # Change to your username
            password='Jio@2024',    # Change to your password
            database='newsschema'   # Change to your database name
        )
        if connection.is_connected():
            print("Connection successful!")
            db_info = connection.get_server_info()
            print("MySQL Server version:", db_info)
            # Optional: You can also execute a test query
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM extractednews WHERE Published IS NULL ORDER BY Published DESC")
            record = cursor.fetchone()
            print("You're connected to the database:", record)
    except Error as e:
        print("Error while connecting to MySQL:", str(e))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
 
# Call the function to check the connection
check_database_connection()