from PIL import Image
import rawpy
import io

def generate_thumbnail_data(image_path: str, size: tuple = (256, 256)) -> bytes | None:
    """Generates a thumbnail from an image file and returns it as bytes."""
    try:
        if image_path.lower().endswith('.cr3'):
            with rawpy.imread(image_path) as raw:
                rgb = raw.postprocess()
                img = Image.fromarray(rgb)
        else:
            img = Image.open(image_path)
        
        img.thumbnail(size, Image.LANCZOS)
        
        # Convert PIL Image to bytes
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        return byte_arr.getvalue()

    except Exception as e:
        print(f"Error generating thumbnail for {image_path}: {e}")
        return None
