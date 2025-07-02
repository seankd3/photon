from PIL import Image
from PyQt5.QtGui import QPixmap, QImage

def generate_thumbnail(image_path: str, size: tuple = (256, 256)) -> QPixmap | None:
    """Generates a thumbnail from an image file and returns it as a QPixmap."""
    try:
        img = Image.open(image_path)
        img.thumbnail(size, Image.LANCZOS)
        
        # Convert PIL Image to QImage
        if img.mode == "RGB":
            qimage = QImage(img.tobytes(), img.size[0], img.size[1], QImage.Format_RGB888)
        elif img.mode == "RGBA":
            qimage = QImage(img.tobytes(), img.size[0], img.size[1], QImage.Format_RGBA8888)
        else:
            qimage = QImage(img.tobytes(), img.size[0], img.size[1], QImage.Format_RGB888) # Default to RGB

        pixmap = QPixmap.fromImage(qimage)
        return pixmap
    except Exception as e:
        print(f"Error generating thumbnail for {image_path}: {e}")
        return None
