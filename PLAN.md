## Photon Project Plan (Python/PyQt6)

**Project Goal:** To create a lightning-fast photo culling application, serving as a modern alternative to Lightroom Classic, with a flexible, dockable UI inspired by Blender, VS Code, and Obsidian.

**Technology Stack:**
*   **Language:** Python 3
*   **GUI Framework:** PyQt6
*   **Image Processing:** Pillow (PIL Fork)
*   **Database Interaction:** `sqlite3` (built-in Python module)

---

### Phase 1: Project Setup & Core Structure

1.  **Create Project Directory:** Established the root `Photon` directory. **(DONE)**
2.  **Initialize Virtual Environment:** Set up a Python virtual environment for isolated dependency management. **(DONE)**
3.  **Define Dependencies:** Created `requirements.txt` to list `PyQt6` and `Pillow`. **(DONE)**
4.  **Install Dependencies:** Installed packages from `requirements.txt`. **(DONE)**
5.  **Initial `GEMINI.md`:** Created this documentation file within the project, outlining the plan and tracking progress. **(DONE)**
6.  **Scaffold Main Application:** Create `main.py` (entry point) and `photon_app.py` (main `QMainWindow` setup). **(DONE)**
7.  **Initial Build/Run Test:** Verified the basic PyQt6 window launches successfully. **(DONE)**

---

### Phase 2: Data Layer - Lightroom Catalog Reading

1.  **Models (`photon/models.py`):**
    *   Implement `FolderNode` (for folder hierarchy). **(DONE)**
    *   Implement `PhotoMetadata` (for photo details). **(DONE)**
    *   Implement `LightroomCatalog` (to hold the entire catalog structure). **(DONE)**
2.  **Catalog Reader (`photon/catalog_reader.py`):**
    *   Develop `LightroomCatalogReader` class. **(DONE)**
    *   Implement methods to connect to `.lrcat` SQLite databases. **(DONE)**
    *   Write SQL queries to extract folder structure (`AgLibraryFolder`) and photo metadata (`AgLibraryFile`, `Adobe_images`). **(DONE)**
    *   Implement robust date parsing for Lightroom's unique date formats. **(DONE)**
    *   Handle potential errors (e.g., file not found, database corruption). **(DONE)**
3.  **Unit Tests:** Write tests for `catalog_reader.py` to ensure accurate data extraction and parsing. **(DONE)**

---

### Phase 3: Image Processing & Caching

1.  **Image Processor (`photon/image_processor.py`):**
    *   Implement `ImageProcessor` class. **(DONE)**
    *   Develop methods for generating thumbnails from various image formats using Pillow. **(DONE)**
    *   Implement a caching mechanism for thumbnails (on-disk, to avoid regenerating them). **(DONE)**
    *   Handle image loading for the main preview panel. **(DONE)**
2.  **Unit Tests:** Write tests for `image_processor.py` to verify thumbnail generation and caching. **(DONE)**

---

### Phase 4: User Interface (UI) Implementation

1.  **Main Window (`photon/photon_app.py`):**
    *   Set up `QMainWindow` as the main application window.
    *   Integrate `QDockWidget`s for flexible, rearrangeable panels.
    *   Implement initial dark theme using QSS (Qt Style Sheets).
2.  **Panel Views (`photon/views/`):
    *   **Folder Tree View (`folder_tree_view.py`):** Display the `FolderNode` hierarchy. **(DONE)**
    *   **Thumbnail Grid View (`thumbnail_grid_view.py`):** Efficiently display `PhotoMetadata` thumbnails. Implement virtual scrolling for large datasets.
    *   **Photo Preview View (`photo_preview_view.py`):** Display the selected photo at a larger size with metadata overlay.
3.  **Data Binding/Communication:** Establish communication between the `catalog_reader`, `image_processor`, and UI views using PyQt's signal/slot mechanism. **(DONE)**
4.  **Interaction:** Implement basic keyboard navigation and culling actions (e.g., rating, pick/reject). **(DONE)**

---

### Phase 5: Testing, Verification & Refinement

1.  **Integration Tests:** Test the flow from catalog loading to UI display.
2.  **Performance Profiling:** Identify and optimize bottlenecks in data loading and image rendering.
3.  **Error Handling:** Implement comprehensive error handling and user feedback mechanisms.
4.  **UI Polish:** Refine the dark theme, ensure responsiveness, and enhance user experience.
5.  **Documentation Update:** Continuously update `GEMINI.md` with implementation details, usage instructions, and any known issues or future enhancements.
