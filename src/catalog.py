import os
import sqlite3


def get_images(catalog_path: str) -> list:
    """Connects to the Lightroom catalog and retrieves image data."""
    try:
        # Connect in read-only mode
        con = sqlite3.connect(f'file:{catalog_path}?mode=ro', uri=True)
        cur = con.cursor()

        # This query joins the image table with the file table to get the file paths
        cur.execute(
            """
            SELECT
                img.id_local,
                file.baseName || '.' || file.extension AS fileName,
                folder.pathFromRoot || file.baseName || '.' || file.extension AS relativePath,
                rootFolder.absolutePath || folder.pathFromRoot || file.baseName || '.' || file.extension AS absolutePath
            FROM Adobe_images img
            JOIN AgLibraryFile file ON img.rootFile = file.id_local
            JOIN AgLibraryFolder folder ON file.folder = folder.id_local
            JOIN AgLibraryRootFolder rootFolder ON folder.rootFolder = rootFolder.id_local;
            """
        )
        images = cur.fetchall()
        con.close()
        return images
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def get_pick_status(catalog_path: str) -> list:
    """Retrieves the pick/reject status of all images."""
    try:
        con = sqlite3.connect(f'file:{catalog_path}?mode=ro', uri=True)
        cur = con.cursor()

        cur.execute(
            """
            SELECT
                file.baseName || '.' || file.extension AS fileName,
                img.pick
            FROM Adobe_images img
            JOIN AgLibraryFile file ON img.rootFile = file.id_local;
            """
        )
        images = cur.fetchall()
        con.close()
        return images
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def update_rating(catalog_path: str, image_id: int, rating: int) -> bool:
    """Updates the rating for a specific image in the catalog."""
    try:
        # Connect in read-write mode
        con = sqlite3.connect(catalog_path)
        cur = con.cursor()

        cur.execute(
            "UPDATE Adobe_images SET rating = ? WHERE id_local = ?", (rating, image_id)
        )
        con.commit()
        con.close()
        print(f"Successfully updated rating for image {image_id} to {rating}.")
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def get_last_modified(file_path: str) -> float | None:
    """Returns the last modification timestamp of a file."""
    try:
        return os.path.getmtime(file_path)
    except OSError as e:
        print(f"Error getting file modification time: {e}")
        return None
