from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from photon.models import PhotoMetadata
from photon.image_processor import ImageProcessor
from typing import Optional
import os


class PhotoPreviewView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.catalog = None
        self.current_photo = None
        self.image_processor = ImageProcessor()

        layout = QVBoxLayout(self)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)

        self.metadata_label = QLabel("No photo selected.")
        self.metadata_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        layout.addWidget(self.metadata_label)

        self.setLayout(layout)

        self.setStyleSheet(
            """
            PhotoPreviewView {
                background-color: #3E3E40;
                color: #CCCCCC;
                border: none;
            }
            QLabel {
                color: #CCCCCC;
            }
        """
        )

    def set_catalog(self, catalog: LightroomCatalog):
        self.catalog = catalog
        self.set_photo(None)  # Clear preview when catalog changes

    def set_photo(self, photo: PhotoMetadata):
        self.current_photo = photo
        if photo:
            # Load and display image
            image = self.image_processor.load_image(photo.file_path)
            if image:
                pixmap = QPixmap.fromImage(image)
                self.image_label.setPixmap(
                    pixmap.scaled(
                        self.image_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                self.image_label.adjustSize()
            else:
                self.image_label.clear()
                self.image_label.setText("Could not load image.")

            # Display metadata
            file_name_without_ext, file_extension = os.path.splitext(photo.file_name)
            metadata_text = f"<b>File:</b> {file_name_without_ext}{file_extension}<br>"
            metadata_text += f"<b>Folder:</b> {photo.folder_id}<br>"
            metadata_text += f"<b>Captured:</b> {photo.date_captured.strftime('%Y-%m-%d %H:%M:%S') if photo.date_captured else 'N/A'}<br>"
            metadata_text += f"<b>Dimensions:</b> {photo.width}x{photo.height}<br>"
            metadata_text += f"<b>Rating:</b> {photo.rating} stars<br>"
            metadata_text += f"<b>Picked:</b> {'Yes' if photo.is_picked else 'No'}<br>"
            metadata_text += f"<b>Color Label:</b> {photo.color_label}<br>"
            metadata_text += (
                f"<b>Camera:</b> {photo.camera_make} {photo.camera_model}<br>"
            )
            metadata_text += f"<b>Lens:</b> {photo.lens_model}<br>"
            metadata_text += f"<b>ISO:</b> {photo.iso}<br>"
            metadata_text += f"<b>Aperture:</b> f/{photo.aperture}<br>"
            metadata_text += f"<b>Shutter:</b> {photo.shutter_speed}<br>"
            self.metadata_label.setText(metadata_text)
        else:
            self.image_label.clear()
            self.metadata_label.setText("No photo selected.")

    def update_culling_status(self, photo: PhotoMetadata):
        if photo and photo == self.current_photo:
            self.set_photo(photo)  # Re-render the metadata

    @property
    def current_photo_id(self) -> str | None:
        return self.current_photo.id if self.current_photo else None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_photo and self.image_label.pixmap():
            self.image_label.setPixmap(
                self.image_label.pixmap().scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
