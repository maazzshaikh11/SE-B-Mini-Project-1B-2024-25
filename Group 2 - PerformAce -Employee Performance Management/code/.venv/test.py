import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='TuViZa@2345',
        database='UserManagement',
        port=3306
    )
    if conn.is_connected():
        print("Successfully connected to the database")
    conn.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")
