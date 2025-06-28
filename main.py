import sys
from PyQt6.QtWidgets import QApplication, QFileDialog
from photon_app import PhotonApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotonApp()
    window.showMaximized()

    # Allow user to select a catalog
    catalog_path, _ = QFileDialog.getOpenFileName(
        window, "Open Lightroom Catalog", "", "Lightroom Catalog Files (*.lrcat)"
    )
    if catalog_path:
        window.load_catalog(catalog_path)

    sys.exit(app.exec())
