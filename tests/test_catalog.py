import sqlite3


def get_images(catalog_path):
    """Connects to the Lightroom catalog and retrieves image data."""
    try:
        con = sqlite3.connect(f'file:{catalog_path}?mode=ro', uri=True)
        cur = con.cursor()

        # This query joins the image table with the file table to get the file paths
        cur.execute(
            """
            SELECT
                img.id_local,
                file.baseName || '.' || file.extension AS fileName,
                folder.pathFromRoot || file.baseName || '.' || file.extension AS relativePath
            FROM Adobe_images img
            JOIN AgLibraryFile file ON img.rootFile = file.id_local
            JOIN AgLibraryFolder folder ON file.folder = folder.id_local;
            """
        )
        images = cur.fetchall()
        con.close()
        return images
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


if __name__ == '__main__':
    catalog_path = "C:/Users/smast/OneDrive/Desktop/CodeProjects/Photon/TestCatolog/2025.lrcat"
    images = get_images(catalog_path)
    if images:
        print(f"Found {len(images)} images.")
        # for image in images:
        #     print(image)
