from datetime import datetime
from typing import List, Optional, Dict, Set

class PhotoMetadata:
    def __init__(self,
                 id: str,
                 file_path: str,
                 file_name: str,
                 folder_id: str,
                 file_format: str,
                 file_size: int,
                 date_created: datetime,
                 date_modified: datetime,
                 date_captured: Optional[datetime] = None,
                 width: int = 0,
                 height: int = 0,
                 orientation: str = "",
                 camera_make: str = "",
                 camera_model: str = "",
                 lens_model: str = "",
                 focal_length: Optional[float] = None,
                 aperture: Optional[float] = None,
                 shutter_speed: Optional[float] = None,
                 iso: Optional[int] = None,
                 rating: int = 0,
                 color_label: str = "",
                 is_picked: bool = False,
                 is_rejected: bool = False,
                 keywords: Optional[List[str]] = None,
                 collections: Optional[List[str]] = None,
                 thumbnail_path: Optional[str] = None,
                 thumbnail_generated_at: Optional[datetime] = None):

        self.id = id
        self.file_path = file_path
        self.file_name = file_name
        self.folder_id = folder_id
        self.file_format = file_format
        self.file_size = file_size
        self.date_created = date_created
        self.date_modified = date_modified
        self.date_captured = date_captured
        self.width = width
        self.height = height
        self.orientation = orientation
        self.camera_make = camera_make
        self.camera_model = camera_model
        self.lens_model = lens_model
        self.focal_length = focal_length
        self.aperture = aperture
        self.shutter_speed = shutter_speed
        self.iso = iso
        self.rating = rating
        self.color_label = color_label
        self.is_picked = is_picked
        self.is_rejected = is_rejected
        self.keywords = keywords if keywords is not None else []
        self.collections = collections if collections is not None else []
        self.thumbnail_path = thumbnail_path
        self.thumbnail_generated_at = thumbnail_generated_at

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height if self.height > 0 else 0

    @property
    def has_thumbnail(self) -> bool:
        return self.thumbnail_path is not None and self.thumbnail_generated_at is not None


class FolderNode:
    def __init__(self,
                 id: str,
                 name: str,
                 full_path: str,
                 parent_id: Optional[str] = None,
                 parent: Optional['FolderNode'] = None):
        self.id = id
        self.name = name
        self.full_path = full_path
        self.parent_id = parent_id
        self.parent = parent
        self.children: List['FolderNode'] = []
        self.photos: List[PhotoMetadata] = []

        self.is_expanded: bool = False
        self.is_selected: bool = False
        self.is_loading: bool = False

    @property
    def photo_count(self) -> int:
        return len(self.photos)

    @property
    def total_photo_count(self) -> int:
        return self.photo_count + sum(c.total_photo_count for c in self.children)

    @property
    def is_root(self) -> bool:
        return self.parent is None

    @property
    def has_children(self) -> bool:
        return len(self.children) > 0

    @property
    def has_photos(self) -> bool:
        return len(self.photos) > 0

    @property
    def level(self) -> int:
        return (self.parent.level + 1) if self.parent else 0

    def get_all_descendants(self) -> List['FolderNode']:
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants

    def get_all_photos(self) -> List[PhotoMetadata]:
        all_photos = list(self.photos)
        for child in self.children:
            all_photos.extend(child.get_all_photos())
        return all_photos

    def find_child(self, name: str) -> Optional['FolderNode']:
        for child in self.children:
            if child.name.lower() == name.lower():
                return child
        return None

    def add_child(self, child: 'FolderNode'):
        child.parent = self
        child.parent_id = self.id
        self.children.append(child)

    def __str__(self) -> str:
        return self.name


class LightroomCatalog:
    def __init__(self,
                 file_path: str,
                 name: str,
                 last_modified: datetime,
                 loaded_at: datetime,
                 version: str = ""):
        self.file_path = file_path
        self.name = name
        self.last_modified = last_modified
        self.loaded_at = loaded_at
        self.version = version

        self.root_folders: List[FolderNode] = []
        self.photos_by_id: Dict[str, PhotoMetadata] = {}
        self.folders_by_id: Dict[str, FolderNode] = {}

        self.supported_formats: Set[str] = {
            ".jpg", ".jpeg", ".png", ".dng", ".cr2", ".cr3", ".nef", ".arw", ".orf", ".rw2"
        }

    @property
    def total_photo_count(self) -> int:
        return len(self.photos_by_id)

    @property
    def total_folder_count(self) -> int:
        return len(self.folders_by_id)

    @property
    def total_file_size(self) -> int:
        return sum(p.file_size for p in self.photos_by_id.values())

    def get_all_photos(self) -> List[PhotoMetadata]:
        return list(self.photos_by_id.values())

    def get_all_folders(self) -> List[FolderNode]:
        return list(self.folders_by_id.values())

    def find_photo(self, id: str) -> Optional[PhotoMetadata]:
        return self.photos_by_id.get(id)

    def find_folder(self, id: str) -> Optional[FolderNode]:
        return self.folders_by_id.get(id)

    def search_photos(self, search_term: str) -> List[PhotoMetadata]:
        if not search_term or not search_term.strip():
            return []

        term = search_term.lower()
        return [p for p in self.photos_by_id.values() if
                term in p.file_name.lower() or
                term in p.file_path.lower() or
                any(term in k.lower() for k in p.keywords)]

    def get_filtered_photos(
        self,
        format: Optional[str] = None,
        min_rating: Optional[int] = None,
        is_picked: Optional[bool] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[PhotoMetadata]:
        query = list(self.photos_by_id.values())

        if format:
            query = [p for p in query if p.file_format.lower() == format.lower()]

        if min_rating is not None:
            query = [p for p in query if p.rating >= min_rating]

        if is_picked is not None:
            query = [p for p in query if p.is_picked == is_picked]

        if from_date:
            query = [p for p in query if p.date_captured and p.date_captured >= from_date]

        if to_date:
            query = [p for p in query if p.date_captured and p.date_captured <= to_date]

        return query

    def is_format_supported(self, extension: str) -> bool:
        return extension.lower() in self.supported_formats

    def __str__(self) -> str:
        return self.name
