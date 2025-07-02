import os
import sqlite3
import pytest
from src.catalog import get_images, get_pick_status, update_rating, get_last_modified

# Create a dummy Lightroom catalog for testing
@pytest.fixture(scope="module")
def dummy_catalog(tmpdir_factory):
    catalog_path = tmpdir_factory.mktemp("data").join("test.lrcat")
    conn = sqlite3.connect(str(catalog_path))
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE Adobe_images (id_local INTEGER PRIMARY KEY, rating INTEGER, pick INTEGER, rootFile INTEGER)")
    cursor.execute("CREATE TABLE AgLibraryFile (id_local INTEGER PRIMARY KEY, baseName TEXT, extension TEXT, folder INTEGER)")
    cursor.execute("CREATE TABLE AgLibraryFolder (id_local INTEGER PRIMARY KEY, pathFromRoot TEXT)")
    
    cursor.execute("INSERT INTO AgLibraryFolder (id_local, pathFromRoot) VALUES (?, ?)", (1, "/test_folder/"))
    cursor.execute("INSERT INTO AgLibraryFile (id_local, baseName, extension, folder) VALUES (?, ?, ?, ?)", (1, "image1", "jpg", 1))
    cursor.execute("INSERT INTO Adobe_images (id_local, rating, pick, rootFile) VALUES (?, ?, ?, ?)", (1, 3, 1, 1))
    cursor.execute("INSERT INTO AgLibraryFile (id_local, baseName, extension, folder) VALUES (?, ?, ?, ?)", (2, "image2", "png", 1))
    cursor.execute("INSERT INTO Adobe_images (id_local, rating, pick, rootFile) VALUES (?, ?, ?, ?)", (2, 0, 0, 2))
    cursor.execute("INSERT INTO AgLibraryFile (id_local, baseName, extension, folder) VALUES (?, ?, ?, ?)", (3, "image3", "gif", 1))
    cursor.execute("INSERT INTO Adobe_images (id_local, rating, pick, rootFile) VALUES (?, ?, ?, ?)", (3, 5, 1, 3))
    conn.commit()
    conn.close()
    return str(catalog_path)

def test_get_images(dummy_catalog):
    images = get_images(dummy_catalog)
    assert len(images) == 3
    assert images[0][0] == 1
    assert images[0][1] == "image1.jpg"

def test_get_pick_status(dummy_catalog):
    pick_status = get_pick_status(dummy_catalog)
    assert len(pick_status) == 3
    assert ("image1.jpg", 1) in pick_status
    assert ("image1.jpg", 0) not in pick_status

def test_update_rating(dummy_catalog):
    update_rating(dummy_catalog, 1, 4)
    conn = sqlite3.connect(dummy_catalog)
    cursor = conn.cursor()
    cursor.execute("SELECT rating FROM Adobe_images WHERE id_local = ?", (1,))
    rating = cursor.fetchone()[0]
    conn.close()
    assert rating == 4

def test_get_last_modified(dummy_catalog):
    initial_mtime = get_last_modified(dummy_catalog)
    assert initial_mtime is not None
    
    # Modify the file to change its modification time
    with open(dummy_catalog, "a") as f:
        f.write("test")
    
    new_mtime = get_last_modified(dummy_catalog)
    assert new_mtime is not None
    assert new_mtime > initial_mtime
