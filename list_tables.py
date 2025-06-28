import sqlite3
import sys

def list_tables(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        return tables
    except sqlite3.Error as e:
        return f"Database error: {e}"

if __name__ == '__main__':
    db_path = r"C:\Users\smast\OneDrive\Desktop\CodeProjects\Photon\TestCatolog\2025 Helper.lrdata\2025 Helper.lrcat"
    print(f"Attempting to list tables in database '{db_path}'")
    tables = list_tables(db_path)
    print(tables)