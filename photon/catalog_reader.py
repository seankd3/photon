import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict

from photon.models import LightroomCatalog, FolderNode, PhotoMetadata
from photon.utils import extract_lrcat_data

class LightroomCatalogReader:
    def __init__(self):
        pass

    async def load_catalog_async(self, catalog_path: str = None, conn: Optional[sqlite3.Connection] = None) -> LightroomCatalog:
        print(f"Loading Lightroom catalog from: {catalog_path}" if catalog_path else "Loading Lightroom catalog from provided connection")

        _conn = None
        if conn is None:
            if not catalog_path:
                raise ValueError("Either catalog_path or conn must be provided.")
            
            # Define a path for the extracted database
            extracted_db_path = os.path.join(os.path.dirname(catalog_path), f"{os.path.basename(catalog_path)}.extracted.db")
            
            # Attempt to extract data if the extracted DB doesn't exist or is older than the lrcat
            if not os.path.exists(extracted_db_path) or os.path.getmtime(extracted_db_path) < os.path.getmtime(catalog_path):
                print(f"Extracting data from {catalog_path} to {extracted_db_path}...".encode('utf-8', 'replace').decode('utf-8'))
                extract_lrcat_data(catalog_path, extracted_db_path)
            
            _conn = sqlite3.connect(extracted_db_path)
        else:
            _conn = conn

        catalog = LightroomCatalog(
            file_path=catalog_path if catalog_path else "",
            name=os.path.splitext(os.path.basename(catalog_path))[0] if catalog_path else "In-memory Catalog",
            last_modified=datetime.fromtimestamp(os.path.getmtime(catalog_path)) if catalog_path and os.path.exists(catalog_path) else datetime.now(),
            loaded_at=datetime.now()
        )

        with _conn as conn_context:
            cursor = conn_context.cursor()

            catalog.version = self._get_catalog_version(cursor)

            folders = self._load_folders(cursor)
            for folder in folders:
                catalog.folders_by_id[folder.id] = folder

            # After building hierarchy, identify true root folders
            for folder in folders:
                if folder.parent is None:
                    catalog.root_folders.append(folder)

            photos = self._load_photos(cursor)
            for photo in photos:
                catalog.photos_by_id[photo.id] = photo
                if photo.folder_id in catalog.folders_by_id:
                    catalog.folders_by_id[photo.folder_id].photos.append(photo)

        print(f"Loaded catalog with {catalog.total_folder_count} folders and {catalog.total_photo_count} photos".encode('utf-8', 'replace').decode('utf-8'))

        return catalog

    def is_valid_catalog(self, catalog_path: str) -> bool:
        if not os.path.exists(catalog_path) or not catalog_path.lower().endswith(".lrcat"):
            return False
        try:
            with sqlite3.connect(catalog_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name IN ('AgLibraryFile', 'AgLibraryFolder', 'Adobe_images')")
                table_count = cursor.fetchone()[0]
                return table_count >= 3
        except sqlite3.Error:
            return False

    def get_catalog_info(self, catalog_path: str) -> Tuple[str, str, datetime, int]:
        with sqlite3.connect(catalog_path) as conn:
            cursor = conn.cursor()

            version = self._get_catalog_version(cursor)
            photo_count = self._get_photo_count(cursor)

        return (
            os.path.splitext(os.path.basename(catalog_path))[0],
            version,
            datetime.fromtimestamp(os.path.getmtime(catalog_path)),
            photo_count
        )

    def _get_catalog_version(self, cursor: sqlite3.Cursor) -> str:
        try:
            cursor.execute("SELECT value FROM AgLibraryPreference WHERE name = 'libraryVersion'")
            result = cursor.fetchone()
            return result[0] if result else "Unknown"
        except sqlite3.Error:
            return "Unknown"

    def _get_photo_count(self, cursor: sqlite3.Cursor) -> int:
        cursor.execute("SELECT COUNT(*) FROM AgLibraryFile WHERE fileFormat IS NOT NULL")
        return cursor.fetchone()[0]

    def _load_folders(self, cursor: sqlite3.Cursor) -> List[FolderNode]:
        folders: List[FolderNode] = []
        folder_lookup: Dict[str, FolderNode] = {}

        cursor.execute("""
            SELECT
                f.id_local as Id,
                f.pathFromRoot as PathFromRoot,
                r.absolutePath as RootAbsolutePath,
                f.parent as ParentId
            FROM AgLibraryFolder f
            JOIN AgLibraryRootFolder r ON f.rootFolder = r.id_local
            ORDER BY f.pathFromRoot
        """)

        # A temporary lookup to get the full path of a parent by its ID
        path_lookup: Dict[str, str] = {}

        for row in cursor.fetchall():
            folder_id = str(row[0])
            path_from_root = row[1]
            root_abs_path = row[2] if row[2] else ""
            parent_id = str(row[3]) if row[3] is not None else None

            full_path = os.path.join(root_abs_path, path_from_root.lstrip('/'))
            path_lookup[folder_id] = path_from_root

            folder_name = path_from_root
            if parent_id and parent_id in path_lookup:
                parent_path = path_lookup[parent_id]
                if path_from_root.startswith(parent_path):
                    folder_name = path_from_root[len(parent_path):]

            folder = FolderNode(
                id=folder_id,
                name=folder_name,
                full_path=full_path,
                parent_id=parent_id
            )
            folders.append(folder)
            folder_lookup[folder.id] = folder

        # Build hierarchy
        for folder in folders:
            if folder.parent_id and folder.parent_id in folder_lookup:
                parent = folder_lookup[folder.parent_id]
                parent.add_child(folder)

        return folders

    def _load_photos(self, cursor: sqlite3.Cursor) -> List[PhotoMetadata]:
        photos: List[PhotoMetadata] = []

        cursor.execute("""
            SELECT 
                f.id_local as Id,
                f.baseName as FileName,
                f.extension as FileExtension,
                f.folder as FolderId,
                f.fileFormat as FileFormat,
                f.fileSize as FileSize,
                f.fileCreateDate as DateCreated,
                f.fileModDate as DateModified,
                i.captureTime as DateCaptured,
                i.fileWidth as Width,
                i.fileHeight as Height,
                i.orientation as Orientation,
                i.cameraMake as CameraMake,
                i.cameraModel as CameraModel,
                i.lens as LensModel,
                i.focalLength as FocalLength,
                i.aperture as Aperture,
                i.shutterSpeed as ShutterSpeed,
                i.isoSpeedRating as Iso,
                i.rating as Rating,
                i.colorLabels as ColorLabel,
                i.pick as IsPicked,
                r.absolutePath as RootFolderAbsolutePath, 
                lf.pathFromRoot as FolderPathFromRoot 
            FROM AgLibraryFile f
            LEFT JOIN Adobe_images i ON f.id_local = i.rootFile
            LEFT JOIN AgLibraryFolder lf ON f.folder = lf.id_local
            LEFT JOIN AgLibraryRootFolder r ON lf.rootFolder = r.id_local 
            WHERE f.fileFormat IS NOT NULL
            ORDER BY i.captureTime DESC
        """)

        for row in cursor.fetchall():
            # Construct full file path
            root_folder_abs_path = row[22] if row[22] else ""
            folder_path_from_root = row[23] if row[23] else ""
            file_name = row[1] if row[1] else ""
            file_extension = row[2] if row[2] else ""

            # Combine root path, path from root, and file name/extension
            # Ensure correct path separators and handle potential double slashes
            full_folder_path = os.path.join(root_folder_abs_path, folder_path_from_root.lstrip('/'))
            file_path = os.path.join(full_folder_path, f"{file_name}.{file_extension}")

            photo = PhotoMetadata(
                id=str(row[0]),
                file_path=file_path,
                file_name=file_name,
                folder_id=str(row[3]) if row[3] is not None else "",
                file_format=row[4] if row[4] else "",
                file_size=row[5] if row[5] else 0,
                date_created=self._parse_lightroom_date(row[6]),
                date_modified=self._parse_lightroom_date(row[7]),
                date_captured=self._parse_lightroom_capture_time(row[8]),
                width=row[9] if row[9] else 0,
                height=row[10] if row[10] else 0,
                orientation=row[11] if row[11] else "",
                camera_make=row[12] if row[12] else "",
                camera_model=row[13] if row[13] else "",
                lens_model=row[14] if row[14] else "",
                focal_length=row[15],
                aperture=row[16],
                shutter_speed=row[17],
                iso=row[18],
                rating=row[19] if row[19] else 0,
                color_label=row[20] if row[20] else "",
                is_picked=bool(row[21]) if row[21] is not None else False
            )
            photos.append(photo)

        return photos

    def _parse_lightroom_date(self, lr_date_seconds: Optional[float]) -> datetime:
        if lr_date_seconds is None:
            return datetime.min
        # Lightroom dates are seconds since 2001-01-01 UTC
        base_date = datetime(2001, 1, 1, 0, 0, 0)
        return base_date + timedelta(seconds=lr_date_seconds)

    def _parse_lightroom_capture_time(self, lr_capture_time_str: Optional[str]) -> Optional[datetime]:
        if lr_capture_time_str is None:
            return None
        try:
            # Lightroom captureTime is typically an ISO 8601 string
            return datetime.fromisoformat(lr_capture_time_str)
        except ValueError:
            return None
