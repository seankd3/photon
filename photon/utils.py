import sqlite3
import os

def extract_lrcat_data(lrcat_path: str, output_db_path: str):
    """
    Extracts relevant data from a Lightroom catalog (.lrcat) into a new SQLite database.
    This is a workaround for cases where the .lrcat file is locked or inaccessible.
    """
    if not os.path.exists(lrcat_path):
        raise FileNotFoundError(f"Lightroom catalog not found at: {lrcat_path}")

    if os.path.exists(output_db_path):
        os.remove(output_db_path)

    try:
        # Connect to the original Lightroom catalog (read-only)
        source_conn = sqlite3.connect(lrcat_path)
        source_cursor = source_conn.cursor()

        # Connect to the new output database
        dest_conn = sqlite3.connect(output_db_path)
        dest_cursor = dest_conn.cursor()

        tables_to_copy = [
            "AgLibraryFile",
            "AgLibraryFolder",
            "Adobe_images",
            "AgLibraryRootFolder",
            "AgLibraryPreference"
        ]

        for table_name in tables_to_copy:
            try:
                # Get schema of the table from the source
                source_cursor.execute(f"PRAGMA table_info({table_name})")
                schema = source_cursor.fetchall()
                if not schema:
                    print(f"Warning: Table {table_name} not found in {lrcat_path}")
                    continue

                # Create table in destination
                columns = ", ".join([f"{col[1]} {col[2]}" for col in schema])
                dest_cursor.execute(f"CREATE TABLE {table_name} ({columns})")

                # Copy data
                source_cursor.execute(f"SELECT * FROM {table_name}")
                rows = source_cursor.fetchall()
                if rows:
                    placeholders = ", ".join(["?" for _ in schema])
                    dest_cursor.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", rows)
                print(f"Copied {len(rows)} rows from {table_name}")

            except sqlite3.Error as e:
                print(f"Error copying table {table_name}: {e}")
                # Continue to next table even if one fails

        dest_conn.commit()
        dest_conn.close()
        source_conn.close()
        print(f"Data extracted to: {output_db_path}")

    except sqlite3.Error as e:
        print(f"Error accessing Lightroom catalog: {e}")
        if os.path.exists(output_db_path):
            os.remove(output_db_path) # Clean up incomplete file
        raise
