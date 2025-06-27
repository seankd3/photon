from PIL import Image
import os

# Ensure the cache directory exists
cache_dir = os.path.join(os.path.dirname(__file__), "cache", "thumbnails")
os.makedirs(cache_dir, exist_ok=True)

# Create a simple red square image as a placeholder
img = Image.new('RGB', (100, 100), color = 'red')
img.save(os.path.join(cache_dir, 'error_thumbnail.png'))
