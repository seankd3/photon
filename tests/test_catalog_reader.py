import unittest
import sqlite3
from datetime import datetime

from photon.catalog_reader import LightroomCatalogReader
from photon.models import LightroomCatalog


class TestLightroomCatalogReader(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        # Create an in-memory SQLite database for testing
        cls.conn = sqlite3.connect(":memory:")
        cls.cursor = cls.conn.cursor()
        cls._create_dummy_lrcat_in_memory(cls.cursor)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    @classmethod
    def _create_dummy_lrcat_in_memory(cls, cursor):
        # Create necessary tables
        cursor.execute(
            """
            CREATE TABLE AgLibraryFile (
                id_local INTEGER PRIMARY KEY,
                baseName TEXT,
                extension TEXT,
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
                rootFolder INTEGER,
                parentId INTEGER
            );
        """
        )
        cursor.execute(
            """
            CREATE TABLE AgLibraryRootFolder (
                id_local INTEGER PRIMARY KEY,
                absolutePath TEXT
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
        # Root Folder
        cursor.execute(
            "INSERT INTO AgLibraryRootFolder (id_local, absolutePath) VALUES (?, ?)",
            (1, "C:/Users/TestUser/Pictures/"),
        )

        # Folders
        cursor.execute(
            "INSERT INTO AgLibraryFolder (id_local, pathFromRoot, rootFolder, parentId) VALUES (?, ?, ?, ?)",
            (1, "Photos/", 1, None),
        )
        cursor.execute(
            "INSERT INTO AgLibraryFolder (id_local, pathFromRoot, rootFolder, parentId) VALUES (?, ?, ?, ?)",
            (2, "Photos/2023/", 1, 1),
        )
        cursor.execute(
            "INSERT INTO AgLibraryFolder (id_local, pathFromRoot, rootFolder, parentId) VALUES (?, ?, ?, ?)",
            (3, "Photos/2024/", 1, 1),
        )

        # Preferences
        cursor.execute(
            "INSERT INTO AgLibraryPreference (name, value) VALUES (?, ?)",
            ("libraryVersion", "12.0"),
        )

        # Photos
        base_date_2001 = datetime(2001, 1, 1, 0, 0, 0)
        file_create_date_1 = (
            datetime(2023, 1, 10, 10, 0, 0) - base_date_2001
        ).total_seconds()
        file_mod_date_1 = (
            datetime(2023, 1, 10, 10, 5, 0) - base_date_2001
        ).total_seconds()
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
            INSERT INTO AgLibraryFile (id_local, baseName, extension, folder, fileFormat, fileSize, fileCreateDate, fileModDate) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                101,
                "image1",
                "jpg",
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
            INSERT INTO AgLibraryFile (id_local, baseName, extension, folder, fileFormat, fileSize, fileCreateDate, fileModDate) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                102,
                "image2",
                "dng",
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

        cls.conn.commit()

    def test_is_valid_catalog(self):
        reader = LightroomCatalogReader()
        # Test with a dummy file path (will fail as it's not a real file)
        self.assertFalse(reader.is_valid_catalog("non_existent.lrcat"))
        # Test with a valid in-memory connection (requires a different test approach)
        # For now, we'll rely on load_catalog_async to test the core logic

    async def test_load_catalog_async(self):
        reader = LightroomCatalogReader()
        catalog = await reader.load_catalog_async(conn=self.conn)

        self.assertIsInstance(catalog, LightroomCatalog)
        self.assertEqual(catalog.name, "In-memory Catalog")
        self.assertEqual(catalog.version, "12.0")
        self.assertEqual(catalog.total_folder_count, 3)
        self.assertEqual(catalog.total_photo_count, 2)

        # Verify folder hierarchy
        self.assertEqual(len(catalog.root_folders), 1)
        root_folder = catalog.root_folders[0]
        self.assertEqual(root_folder.name, "Photos")
        self.assertEqual(len(root_folder.children), 2)

        folder_2023 = catalog.folders_by_id["2"]
        self.assertEqual(folder_2023.name, "2023")
        self.assertEqual(folder_2023.parent.id, "1")

        # Verify photos
        photo1 = catalog.photos_by_id["101"]
        self.assertEqual(photo1.file_name, "image1")
        self.assertEqual(photo1.folder_id, "2")
        self.assertEqual(photo1.rating, 3)
        self.assertEqual(photo1.color_label, "Red")
        self.assertTrue(photo1.is_picked)
        self.assertAlmostEqual(
            photo1.date_captured.timestamp(),
            datetime(2023, 1, 10, 10, 1, 0).timestamp(),
            delta=1,
        )

        photo2 = catalog.photos_by_id["102"]
        self.assertEqual(photo2.file_name, "image2")
        self.assertEqual(photo2.folder_id, "3")
        self.assertEqual(photo2.rating, 0)
        self.assertEqual(photo2.color_label, "")
        self.assertFalse(photo2.is_picked)
        self.assertAlmostEqual(
            photo2.date_captured.timestamp(),
            datetime(2024, 2, 15, 14, 1, 0).timestamp(),
            delta=1,
        )

        # Verify photos are linked to folders
        self.assertEqual(len(folder_2023.photos), 1)
        self.assertEqual(folder_2023.photos[0].id, "101")

    def test_parse_lightroom_date(self):
        reader = LightroomCatalogReader()
        # Test with a known date (seconds since 2001-01-01 UTC)
        test_seconds = (
            datetime(2020, 5, 15, 12, 30, 0) - datetime(2001, 1, 1, 0, 0, 0)
        ).total_seconds()
        parsed_date = reader._parse_lightroom_date(test_seconds)
        self.assertEqual(parsed_date, datetime(2020, 5, 15, 12, 30, 0))
        self.assertEqual(reader._parse_lightroom_date(None), datetime.min)

    def test_parse_lightroom_capture_time(self):
        reader = LightroomCatalogReader()
        # Test with ISO 8601 string
        test_iso_string = "2023-03-20T15:45:30"
        parsed_time = reader._parse_lightroom_capture_time(test_iso_string)
        self.assertEqual(parsed_time, datetime(2023, 3, 20, 15, 45, 30))
        self.assertIsNone(reader._parse_lightroom_capture_time(None))
        self.assertIsNone(reader._parse_lightroom_capture_time("invalid-date"))


if __name__ == "__main__":
    unittest.main()
