import os
import pymssql

def create_connection(server=None, database=None, user=None, password=None):
    """
    Create a connection to SQL Server using pymssql (no ODBC driver required).
    Reads from environment variables if parameters not provided.
    """
    server   = server   or os.environ.get('MSSQL_SERVER',   'localhost')
    database = database or os.environ.get('MSSQL_DATABASE', 'restaurant_management_system')
    user     = user     or os.environ.get('MSSQL_USER',     'sa')
    password = password or os.environ.get('MSSQL_PASSWORD', '')

    try:
        connection = pymssql.connect(
            server=server,
            database=database,
            user=user,
            password=password,
            charset='UTF-8'
        )
        print("✅ SQL Server connection successful")
        return connection
    except Exception as e:
        print(f"❌ Error connecting to SQL Server: {e}")
        return None


def create_connection_trusted(server=None, database=None):
    """
    Connect using Windows Trusted (integrated) authentication.
    Only works on Windows with a local SQL Server instance.
    """
    server   = server   or os.environ.get('MSSQL_SERVER',   r'localhost\SQLEXPRESS')
    database = database or os.environ.get('MSSQL_DATABASE', 'restaurant_management_system')
    try:
        connection = pymssql.connect(
            server=server,
            database=database,
            trusted=True,
            charset='UTF-8'
        )
        print("✅ SQL Server (trusted) connection successful")
        return connection
    except Exception as e:
        print(f"❌ Error connecting to SQL Server (trusted): {e}")
        return None
