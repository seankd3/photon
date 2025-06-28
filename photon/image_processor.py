import os
import rawpy
from PIL import Image
from PyQt6.QtGui import QImage, QPixmap
from typing import Optional, Tuple, Any
import hashlib
from concurrent.futures import ThreadPoolExecutor
import subprocess
from PIL import Image
import typing


class ImageProcessor:
    _executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 1)

    def __init__(self, cache_dir: str = "./cache/thumbnails"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def generate_thumbnail_async(
        self, image_path: str, size: Tuple[int, int] = (256, 256)
    ) -> typing.Any:
        return self._executor.submit(self._generate_thumbnail_sync, image_path, size)

    def _generate_thumbnail_sync(
        self, file_path: str, size: Tuple[int, int]
    ) -> Optional[str]:
        if not os.path.exists(file_path):
            return None

        file_extension = os.path.splitext(file_path)[1].lower()
        image_hash = hashlib.md5(file_path.encode()).hexdigest()
        thumbnail_filename = f"{image_hash}_{size[0]}x{size[1]}.jpg"
        thumbnail_path = os.path.join(self.cache_dir, thumbnail_filename)

        if os.path.exists(thumbnail_path):
            return thumbnail_path

        try:
            if file_extension in [".cr2", ".cr3", ".nef", ".arw", ".orf", ".rw2", ".dng"]:
                with rawpy.imread(file_path) as raw:
                    # Use a smaller size for raw processing to save memory and time
                    # This will be scaled up by Qt later if needed
                    thumb = raw.postprocess(use_camera_wb=True, no_auto_bright=True, output_bps=8)
                    img = Image.fromarray(thumb)
            elif file_extension in [".mp4", ".mov", ".avi", ".mkv"]:
                # Use ffmpeg to extract a frame from the video
                temp_frame_path = os.path.join(self.cache_dir, f"{image_hash}_temp_frame.jpg")
                command = [
                    "ffmpeg",
                    "-i", file_path,
                    "-ss", "00:00:01",  # Seek to 1 second
                    "-vframes", "1",
                    "-q:v", "2",
                    temp_frame_path
                ]
                subprocess.run(command, check=True, capture_output=True)
                img = Image.open(temp_frame_path)
                os.remove(temp_frame_path) # Clean up temp file
            else:
                img = Image.open(file_path)

            img.thumbnail(size, Image.LANCZOS)
            img.save(thumbnail_path, "JPEG")
            return thumbnail_path
        except Exception as e:
            print(f"Error generating thumbnail for {file_path}: {e}")
            return None

    def load_image(self, file_path: str) -> Optional[Image.Image]:
        if not os.path.exists(file_path):
            return None

        file_extension = os.path.splitext(file_path)[1].lower()

        try:
            if file_extension in [".cr2", ".cr3", ".nef", ".arw", ".orf", ".rw2", ".dng"]:
                with rawpy.imread(file_path) as raw:
                    rgb = raw.postprocess(use_camera_wb=True, no_auto_bright=True, output_bps=8)
                    # Convert numpy array to QImage
                    h, w, ch = rgb.shape
                    bytes_per_line = ch * w
                    return Image.fromarray(rgb)
            elif file_extension in [".mp4", ".mov", ".avi", ".mkv"]:
                # For video, we might just return a placeholder or first frame
                # For simplicity, returning None for now, or you can extract a frame
                # and convert it to QImage similar to thumbnail generation.
                return None # Or implement video frame extraction to QImage
            else:
                # For standard image formats, use QImage directly for better performance
                # and to avoid PIL intermediate step if not needed.
                return Image.open(file_path)
        except Exception as e:
            print(f"Error loading image {file_path}: {e}")
            return None
