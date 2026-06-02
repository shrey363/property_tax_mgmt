import mysql.connector
from db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

try:
    print(f"Connecting to {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}...")
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    print("Connection successful!")
    
    # Check tables
    cursor.execute("SHOW TABLES")
    print("Tables:", [r[0] for r in cursor.fetchall()])
    
    # Check procedures
    cursor.execute("SHOW PROCEDURE STATUS WHERE Db = 'property_tax_db'")
    print("Procedures:", [r[1] for r in cursor.fetchall()])
    
    # Check triggers
    cursor.execute("SHOW TRIGGERS")
    print("Triggers:", [r[0] for r in cursor.fetchall()])
    
    cursor.close()
    conn.close()
except Exception as e:
    print("Error:", e)
