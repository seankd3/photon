import sqlite3
import os
from datetime import datetime


def create_dummy_lrcat(db_path):
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create necessary tables
    cursor.execute(
        """
        CREATE TABLE AgLibraryFile (
            id_local INTEGER PRIMARY KEY,
            absolutePath TEXT,
            pathFromRoot TEXT,
            originalFilename TEXT,
            folder INTEGER,
            fileFormat TEXT,
            fileSize INTEGER,
            fileCreateDate REAL,
            fileModDate REAL
        );
    """
    )
    cursor.execute(
        """
        CREATE TABLE AgLibraryFolder (
            id_local INTEGER PRIMARY KEY,
            pathFromRoot TEXT,
            absolutePath TEXT,
            parent INTEGER
        );
    """
    )
    cursor.execute(
        """
        CREATE TABLE Adobe_images (
            id_local INTEGER PRIMARY KEY,
            rootFile INTEGER,
            captureTime TEXT,
            fileWidth INTEGER,
            fileHeight INTEGER,
            orientation TEXT,
            cameraMake TEXT,
            cameraModel TEXT,
            lens TEXT,
            focalLength REAL,
            aperture REAL,
            shutterSpeed REAL,
            isoSpeedRating INTEGER,
            rating INTEGER,
            colorLabels TEXT,
            pick INTEGER
        );
    """
    )
    cursor.execute(
        """
        CREATE TABLE AgLibraryPreference (
            id_local INTEGER PRIMARY KEY,
            name TEXT,
            value TEXT
        );
    """
    )

    # Insert dummy data
    # Folders
    cursor.execute(
        "INSERT INTO AgLibraryFolder (id_local, pathFromRoot, absolutePath, parent) VALUES (?, ?, ?, ?)",
        (1, "Photos/", "C:/Users/TestUser/Pictures/Photos/", None),
    )
    cursor.execute(
        "INSERT INTO AgLibraryFolder (id_local, pathFromRoot, absolutePath, parent) VALUES (?, ?, ?, ?)",
        (2, "Photos/2023/", "C:/Users/TestUser/Pictures/Photos/2023/", 1),
    )
    cursor.execute(
        "INSERT INTO AgLibraryFolder (id_local, pathFromRoot, absolutePath, parent) VALUES (?, ?, ?, ?)",
        (3, "Photos/2024/", "C:/Users/TestUser/Pictures/Photos/2024/", 1),
    )

    # Preferences
    cursor.execute(
        "INSERT INTO AgLibraryPreference (name, value) VALUES (?, ?)",
        ("libraryVersion", "12.0"),
    )

    # Photos
    # Dates are seconds since 2001-01-01 UTC
    base_date_2001 = datetime(2001, 1, 1, 0, 0, 0)
    file_create_date_1 = (
        datetime(2023, 1, 10, 10, 0, 0) - base_date_2001
    ).total_seconds()
    file_mod_date_1 = (datetime(2023, 1, 10, 10, 5, 0) - base_date_2001).total_seconds()
    capture_time_1 = datetime(2023, 1, 10, 10, 1, 0).isoformat()

    file_create_date_2 = (
        datetime(2024, 2, 15, 14, 0, 0) - base_date_2001
    ).total_seconds()
    file_mod_date_2 = (
        datetime(2024, 2, 15, 14, 10, 0) - base_date_2001
    ).total_seconds()
    capture_time_2 = datetime(2024, 2, 15, 14, 1, 0).isoformat()

    cursor.execute(
        """
        INSERT INTO AgLibraryFile (id_local, absolutePath, pathFromRoot, originalFilename, folder, fileFormat, fileSize, fileCreateDate, fileModDate) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            101,
            "C:/Users/TestUser/Pictures/Photos/2023/",
            "image1.jpg",
            "image1.jpg",
            2,
            "JPEG",
            1024000,
            file_create_date_1,
            file_mod_date_1,
        ),
    )
    cursor.execute(
        """
        INSERT INTO Adobe_images (id_local, rootFile, captureTime, fileWidth, fileHeight, orientation, cameraMake, cameraModel, lens, focalLength, aperture, shutterSpeed, isoSpeedRating, rating, colorLabels, pick) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            201,
            101,
            capture_time_1,
            1920,
            1080,
            "Landscape",
            "Canon",
            "EOS R",
            "RF24-105mm",
            50.0,
            4.0,
            0.001,
            400,
            3,
            "Red",
            1,
        ),
    )

    cursor.execute(
        """
        INSERT INTO AgLibraryFile (id_local, absolutePath, pathFromRoot, originalFilename, folder, fileFormat, fileSize, fileCreateDate, fileModDate) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            102,
            "C:/Users/TestUser/Pictures/Photos/2024/",
            "image2.dng",
            "image2.dng",
            3,
            "DNG",
            2048000,
            file_create_date_2,
            file_mod_date_2,
        ),
    )
    cursor.execute(
        """
        INSERT INTO Adobe_images (id_local, rootFile, captureTime, fileWidth, fileHeight, orientation, cameraMake, cameraModel, lens, focalLength, aperture, shutterSpeed, isoSpeedRating, rating, colorLabels, pick) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            202,
            102,
            capture_time_2,
            3000,
            2000,
            "Landscape",
            "Sony",
            "a7 III",
            "FE 24-70mm",
            35.0,
            2.8,
            0.002,
            800,
            0,
            "",
            0,
        ),
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    dummy_db_path = os.path.join(os.path.dirname(__file__), "dummy_catalog.lrcat")
    create_dummy_lrcat(dummy_db_path)
    print(f"Dummy Lightroom catalog created at: {dummy_db_path}")
