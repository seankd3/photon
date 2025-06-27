import sqlite3
import sys

def get_table_schema(db_path, table_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = cursor.fetchall()
        conn.close()
        return schema
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python get_schema.py <db_path> <table_name>")
        sys.exit(1)

    db_path = sys.argv[1]
    table_name = sys.argv[2]
    schema = get_table_schema(db_path, table_name)
    for col in schema:
        print(col)
