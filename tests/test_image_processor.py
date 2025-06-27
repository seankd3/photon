import unittest
import os
from PIL import Image
import hashlib

from photon.image_processor import ImageProcessor

class TestImageProcessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.join(os.path.dirname(__file__), "test_images")
        cls.cache_dir = os.path.join(cls.test_dir, "cache")
        os.makedirs(cls.test_dir, exist_ok=True)
        os.makedirs(cls.cache_dir, exist_ok=True)

        cls.image_processor = ImageProcessor(cache_dir=cls.cache_dir)

        # Create dummy image files
        cls.dummy_image_path_jpg = os.path.join(cls.test_dir, "dummy_image.jpg")
        cls.dummy_image_path_png = os.path.join(cls.test_dir, "dummy_image.png")
        cls._create_dummy_image(cls.dummy_image_path_jpg, "JPEG")
        cls._create_dummy_image(cls.dummy_image_path_png, "PNG")

    @classmethod
    def tearDownClass(cls):
        # Clean up dummy files and cache directory
        if os.path.exists(cls.test_dir):
            import shutil
            shutil.rmtree(cls.test_dir)

    @classmethod
    def _create_dummy_image(cls, path, format):
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save(path, format)

    def test_generate_thumbnail(self):
        thumbnail_path = self.image_processor.generate_thumbnail(self.dummy_image_path_jpg, size=(50, 50))
        self.assertIsNotNone(thumbnail_path)
        self.assertTrue(os.path.exists(thumbnail_path))
        
        # Verify thumbnail size
        with Image.open(thumbnail_path) as thumb_img:
            self.assertEqual(thumb_img.size, (50, 50))

        # Test caching: generating again should return the same path and not re-create
        thumbnail_path_cached = self.image_processor.generate_thumbnail(self.dummy_image_path_jpg, size=(50, 50))
        self.assertEqual(thumbnail_path, thumbnail_path_cached)

        # Test with non-existent image
        non_existent_path = os.path.join(self.test_dir, "non_existent.jpg")
        self.assertIsNone(self.image_processor.generate_thumbnail(non_existent_path))

    def test_load_image(self):
        loaded_image = self.image_processor.load_image(self.dummy_image_path_png)
        self.assertIsNotNone(loaded_image)
        self.assertIsInstance(loaded_image, Image.Image)
        self.assertEqual(loaded_image.size, (100, 100))

        # Test with non-existent image
        non_existent_path = os.path.join(self.test_dir, "non_existent.png")
        self.assertIsNone(self.image_processor.load_image(non_existent_path))

if __name__ == '__main__':
    unittest.main()
