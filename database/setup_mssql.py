"""
SQL Server Database Setup Script
Creates the database and applies the MSSQL schema.
Run this on Windows with SQL Server 2019+ or SQL Server Express.

Usage:
    python database/setup_mssql.py
"""
import os
import sys
import pymssql

def get_connection_params():
    server   = os.environ.get('MSSQL_SERVER',   r'localhost\SQLEXPRESS')
    user     = os.environ.get('MSSQL_USER',     'sa')
    password = os.environ.get('MSSQL_PASSWORD', '')

    if not password:
        print("⚠️  MSSQL_PASSWORD environment variable is not set.")
        print(f"   Server: {server}")
        print(f"   User:   {user}")
        password = input("   Enter SQL Server password: ").strip()
        if not password:
            print("❌ Password is required. Exiting.")
            sys.exit(1)

    return server, user, password


def create_database(server, user, password):
    database = os.environ.get('MSSQL_DATABASE', 'restaurant_management_system')
    print(f"\n📦 Connecting to SQL Server at {server}...")

    try:
        conn = pymssql.connect(
            server=server,
            user=user,
            password=password,
            charset='UTF-8'
        )
        cursor = conn.cursor()
        cursor.execute(f"""
            IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{database}')
            BEGIN
                CREATE DATABASE {database};
            END
        """)
        conn.commit()
        conn.close()
        print(f"✅ Database '{database}' ready.")
        return database
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("   Make sure SQL Server is running and credentials are correct.")
        sys.exit(1)


def apply_schema(server, user, password, database):
    schema_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'database',
        'schema_mssql.sql'
    )

    if not os.path.exists(schema_path):
        print(f"❌ Schema file not found: {schema_path}")
        sys.exit(1)

    print(f"\n📋 Applying schema to database '{database}'...")

    try:
        conn = pymssql.connect(
            server=server,
            database=database,
            user=user,
            password=password,
            charset='UTF-8'
        )
        cursor = conn.cursor()

        with open(schema_path, 'r', encoding='utf-8') as f:
           sql_script = f.read()

        statements = [s.strip() for s in sql_script.split('GO') if s.strip()]

        for stmt in statements:
            if not stmt:
                continue
            cursor.execute(stmt)
            conn.commit()

        conn.close()
        print("✅ Schema applied successfully!")
    except Exception as e:
        print(f"❌ Error applying schema: {e}")
        sys.exit(1)


def verify_connection(server, user, password, database):
    print(f"\n🔍 Verifying connection to '{database}'...")
    try:
        conn = pymssql.connect(
            server=server,
            database=database,
            user=user,
            password=password,
            charset='UTF-8'
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"   Found {len(tables)} tables:")
        for t in tables:
            print(f"   ✅ {t}")
        conn.close()

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        admin_count = cursor.fetchone()[0]
        if admin_count:
            print("\n   Default admin user exists.")
        conn.close()
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    print("=" * 50)
    print("  Restaurant Management System")
    print("  SQL Server Database Setup")
    print("=" * 50)

    server, user, password = get_connection_params()
    database = create_database(server, user, password)
    apply_schema(server, user, password, database)
    verify_connection(server, user, password, database)

    print("\n" + "=" * 50)
    print("  Setup Complete!")
    print("=" * 50)
    print(f"\n  Server:      {server}")
    print(f"  Database:    {database}")
    print(f"  User:        {user}")
    print(f"  Login:       admin / admin123")
    print("\n  Run desktop app with:")
    print("    python main.py")
    print("=" * 50)
