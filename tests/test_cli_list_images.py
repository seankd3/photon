import os
import sqlite3
import pytest
from src.cli import run_cli
from unittest.mock import patch

@pytest.fixture(scope="module")
def setup_in_memory_catalog():
    # Create an in-memory SQLite database
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Create tables with relevant columns and constraints
    cursor.execute("""
        CREATE TABLE AgLibraryRootFolder (
            id_local INTEGER PRIMARY KEY,
            absolutePath TEXT NOT NULL,
            id_global TEXT NOT NULL UNIQUE
        );
    """)
    cursor.execute("""
        CREATE TABLE AgLibraryFolder (
            id_local INTEGER PRIMARY KEY,
            rootFolder INTEGER NOT NULL,
            pathFromRoot TEXT NOT NULL,
            id_global TEXT NOT NULL UNIQUE,
            FOREIGN KEY (rootFolder) REFERENCES AgLibraryRootFolder(id_local)
        );
    """)
    cursor.execute("""
        CREATE TABLE AgLibraryFile (
            id_local INTEGER PRIMARY KEY,
            folder INTEGER NOT NULL,
            baseName TEXT NOT NULL,
            extension TEXT NOT NULL,
            id_global TEXT NOT NULL UNIQUE,
            FOREIGN KEY (folder) REFERENCES AgLibraryFolder(id_local),
            UNIQUE (baseName, extension, folder)
        );
    """)
    cursor.execute("""
        CREATE TABLE Adobe_images (
            id_local INTEGER PRIMARY KEY,
            rootFile INTEGER NOT NULL,
            rating INTEGER,
            pick INTEGER,
            id_global TEXT NOT NULL UNIQUE,
            FOREIGN KEY (rootFile) REFERENCES AgLibraryFile(id_local)
        );
    """)

    # Insert dummy data
    cursor.execute("INSERT INTO AgLibraryRootFolder (id_local, absolutePath, id_global) VALUES (?, ?, ?)", (1, "C:\\test_photos\\", "root_global_id_1"))
    cursor.execute("INSERT INTO AgLibraryFolder (id_local, rootFolder, pathFromRoot, id_global) VALUES (?, ?, ?, ?)", (1, 1, "test_folder\\", "folder_global_id_1"))

    cursor.execute("INSERT INTO AgLibraryFile (id_local, folder, baseName, extension, id_global) VALUES (?, ?, ?, ?, ?)", (101, 1, "test_image_1", "jpg", "file_global_id_101"))
    cursor.execute("INSERT INTO Adobe_images (id_local, rootFile, rating, pick, id_global) VALUES (?, ?, ?, ?, ?)", (201, 101, 3, 1, "image_global_id_201")) # Picked, 3 stars

    cursor.execute("INSERT INTO AgLibraryFile (id_local, folder, baseName, extension, id_global) VALUES (?, ?, ?, ?, ?)", (102, 1, "test_image_2", "jpg", "file_global_id_102"))
    cursor.execute("INSERT INTO Adobe_images (id_local, rootFile, rating, pick, id_global) VALUES (?, ?, ?, ?, ?)", (202, 102, 0, 2, "image_global_id_202")) # Rejected, 0 stars

    cursor.execute("INSERT INTO AgLibraryFile (id_local, folder, baseName, extension, id_global) VALUES (?, ?, ?, ?, ?)", (103, 1, "test_image_3", "jpg", "file_global_id_103"))
    cursor.execute("INSERT INTO Adobe_images (id_local, rootFile, rating, pick, id_global) VALUES (?, ?, ?, ?, ?)", (203, 103, 5, 0, "image_global_id_203")) # Unflagged, 5 stars

    conn.commit()
    yield conn # Yield the connection for use in tests
    conn.close()

@patch('sys.stdout')
def test_list_images_no_filter(mock_stdout, setup_in_memory_catalog):
    with patch('src.catalog.sqlite3.connect', return_value=setup_in_memory_catalog):
        run_cli(['dummy_catalog.lrcat', 'list'])
        output = mock_stdout.getvalue()
        assert "Found 3 images matching the criteria:" in output
        assert "ID: 201, File: test_image_1.jpg, Rating: 3, Pick: 1" in output
        assert "ID: 202, File: test_image_2.jpg, Rating: 0, Pick: 2" in output
        assert "ID: 203, File: test_image_3.jpg, Rating: 5, Pick: 0" in output

@patch('sys.stdout')
def test_list_images_filter_rating(mock_stdout, setup_in_memory_catalog):
    with patch('src.catalog.sqlite3.connect', return_value=setup_in_memory_catalog):
        run_cli(['dummy_catalog.lrcat', 'list', '--rating', '3'])
        output = mock_stdout.getvalue()
        assert "Found 1 images matching the criteria:" in output
        assert "ID: 201, File: test_image_1.jpg, Rating: 3, Pick: 1" in output
        assert "ID: 202" not in output
        assert "ID: 203" not in output

@patch('sys.stdout')
def test_list_images_filter_flag_picked(mock_stdout, setup_in_memory_catalog):
    with patch('src.catalog.sqlite3.connect', return_value=setup_in_memory_catalog):
        run_cli(['dummy_catalog.lrcat', 'list', '--flag', 'picked'])
        output = mock_stdout.getvalue()
        assert "Found 1 images matching the criteria:" in output
        assert "ID: 201, File: test_image_1.jpg, Rating: 3, Pick: 1" in output
        assert "ID: 202" not in output
        assert "ID: 203" not in output

@patch('sys.stdout')
def test_list_images_filter_flag_rejected(mock_stdout, setup_in_memory_catalog):
    with patch('src.catalog.sqlite3.connect', return_value=setup_in_memory_catalog):
        run_cli(['dummy_catalog.lrcat', 'list', '--flag', 'rejected'])
        output = mock_stdout.getvalue()
        assert "Found 1 images matching the criteria:" in output
        assert "ID: 202, File: test_image_2.jpg, Rating: 0, Pick: 2" in output
        assert "ID: 201" not in output
        assert "ID: 203" not in output

@patch('sys.stdout')
def test_list_images_filter_flag_unflagged(mock_stdout, setup_in_memory_catalog):
    with patch('src.catalog.sqlite3.connect', return_value=setup_in_memory_catalog):
        run_cli(['dummy_catalog.lrcat', 'list', '--flag', 'unflagged'])
        output = mock_stdout.getvalue()
        assert "Found 1 images matching the criteria:" in output
        assert "ID: 203, File: test_image_3.jpg, Rating: 5, Pick: 0" in output
        assert "ID: 201" not in output
        assert "ID: 202" not in output

@patch('sys.stdout')
def test_list_images_no_match(mock_stdout, setup_in_memory_catalog):
    with patch('src.catalog.sqlite3.connect', return_value=setup_in_memory_catalog):
        run_cli(cli_args=['dummy_catalog.lrcat', 'list', '--rating', '1', '--flag', 'picked'])
        output = mock_stdout.getvalue()
        print(f"\n--- Actual Output (no match) ---\n{output}--- End Actual Output ---")
        assert "No images found matching the criteria." in output.strip()
        assert "Found" not in output.strip()