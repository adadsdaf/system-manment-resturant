import os
import psycopg2
import psycopg2.extras

def get_db():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    return conn

def query(sql, params=None, fetchone=False, fetchall=False, commit=False):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params or ())
        if commit:
            conn.commit()
            return cur.rowcount
        if fetchone:
            return cur.fetchone()
        if fetchall:
            return cur.fetchall()
        return None
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def query_scalar(sql, params=None):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()
