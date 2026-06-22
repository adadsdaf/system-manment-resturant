import pyodbc

def create_connection():
    try:
        connection = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=DESKTOP-D7O9PME\\SQLEXPRESS;"
            "DATABASE=restaurant_management_system;"
            "Trusted_Connection=yes;"
        )
        print("Database connection successful")
        return connection
    except pyodbc.Error as e:
        print(f"Error connecting to SQL Server: {e}")
        return None