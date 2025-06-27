import os
from PIL import Image
from typing import Optional, Tuple
import hashlib

class ImageProcessor:
    def __init__(self, cache_dir: str = "./cache/thumbnails"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def generate_thumbnail(self, image_path: str, size: Tuple[int, int] = (256, 256)) -> Optional[str]:
        if not os.path.exists(image_path):
            return None

        # Create a unique filename for the thumbnail based on image path and size
        image_hash = hashlib.md5(image_path.encode()).hexdigest()
        thumbnail_filename = f"{image_hash}_{size[0]}x{size[1]}.jpg"
        thumbnail_path = os.path.join(self.cache_dir, thumbnail_filename)

        if os.path.exists(thumbnail_path):
            return thumbnail_path # Return cached thumbnail if it exists

        try:
            with Image.open(image_path) as img:
                img.thumbnail(size, Image.LANCZOS)
                img.save(thumbnail_path, "JPEG")
            return thumbnail_path
        except Exception as e:
            print(f"Error generating thumbnail for {image_path}: {e}")
            return None

    def load_image(self, image_path: str) -> Optional[Image.Image]:
        if not os.path.exists(image_path):
            return None
        try:
            return Image.open(image_path)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None