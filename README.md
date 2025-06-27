# Photon: A Lightning-Fast Photo Culling App

Photon is a desktop application for professional and amateur photographers to quickly cull (rate, sort, and tag) large batches of photos. It is designed to be a modern, fast, and intuitive alternative to the culling process in Adobe Lightroom Classic.

## Features

*   **Blazing Fast Performance:** Photon is built for speed. It loads and displays images and thumbnails with minimal delay, even with large photo libraries.
*   **Lightroom Catalog Integration:** Photon can read your existing Adobe Lightroom catalogs (`.lrcat` files), so you can seamlessly integrate it into your current workflow.
*   **Flexible, Dockable UI:** Inspired by professional tools like Blender and Visual Studio Code, Photon's user interface is composed of dockable panels that you can rearrange to fit your needs.
*   **Essential Culling Tools:**
    *   **Star Ratings:** Assign star ratings (1-5) to your photos.
    *   **Pick/Reject Flags:** Mark photos as "picked" or "rejected".
    *   **Color Labels:** Apply color labels for easy categorization.
*   **Non-Destructive Editing:** All metadata changes (ratings, flags, etc.) are stored in a separate database, leaving your original files untouched.

## Getting Started

### Prerequisites

*   Python 3.10 or later
*   Pip (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/photon.git
    cd photon
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running Photon

To launch the application, run the following command from the project's root directory:

```bash
python main.py
```

## Development

### Running Tests

Photon uses `pytest` for automated testing. To run the test suite, execute the following command:

```bash
pytest
```

### Code Style

This project adheres to the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide. We use `black` for automated code formatting and `ruff` for linting.

### Technology Stack

*   **Python 3:** The core programming language.
*   **PyQt6:** The GUI framework for the desktop application.
*   **Pillow:** A powerful image processing library for Python.
*   **SQLite3:** The database engine for reading Lightroom catalogs and storing application data.

## Contributing

We welcome contributions from the community! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to the project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
