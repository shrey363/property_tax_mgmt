# ============================================================
#  Property Tax Management System
#  File: frontend/db_config.py
#  Description: MySQL connection helper
# ============================================================

import mysql.connector
from mysql.connector import Error

# ── Change these to match your MySQL installation ──────────
DB_HOST     = "127.0.0.1"
DB_PORT     = 3306
DB_NAME     = "property_tax_db"
DB_USER     = "root"
DB_PASSWORD = "8520"         # <-- update with your password
# ───────────────────────────────────────────────────────────


def get_connection():
    """Return a new MySQL connection or raise an exception."""
    conn = mysql.connector.connect(
        host     = DB_HOST,
        port     = DB_PORT,
        database = DB_NAME,
        user     = DB_USER,
        password = DB_PASSWORD,
        autocommit = False,
    )
    return conn


def execute_query(query: str, params: tuple = (), fetch: bool = False):
    """
    Execute a query.
    - If fetch=True  : returns list of rows (SELECT)
    - If fetch=False : commits and returns rowcount (INSERT/UPDATE/DELETE)
    Raises Exception on error.
    """
    conn   = None
    cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        if fetch:
            rows = cursor.fetchall()
            return rows
        else:
            conn.commit()
            return cursor.rowcount
    except Error as e:
        if conn:
            conn.rollback()
        raise Exception(f"Database error: {e}") from e
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def call_procedure(proc_name: str, args: tuple = ()):
    """
    Call a stored procedure.
    Returns (out_args, result_sets).
    """
    conn   = None
    cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        result_args = cursor.callproc(proc_name, args)
        result_sets = []
        for rs in cursor.stored_results():
            result_sets.append(rs.fetchall())
        conn.commit()
        return result_args, result_sets
    except Error as e:
        if conn:
            conn.rollback()
        raise Exception(f"Procedure error: {e}") from e
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def verify_connection():
    """Returns True if DB is reachable, False otherwise."""
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception:
        return False
