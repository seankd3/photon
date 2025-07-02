# Code Standards

This document outlines the coding standards and conventions for the Photon project.

## Python

*   **Style Guide:** Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/).
*   **Formatter:** Use `black` for automated code formatting.
*   **Linter:** Use `flake8` or `ruff` for identifying style and error issues.
*   **Typing:** Use type hints for all function signatures. Run `mypy` for static type checking.
*   **Naming:**
    *   `snake_case` for variables, functions, and methods.
    *   `PascalCase` for classes.
    *   `UPPER_SNAKE_CASE` for constants.
*   **Docstrings:** Use Google-style docstrings.

## Qt

*   **UI Files:** If using Qt Designer, `.ui` files should be stored in a `src/ui/` directory.
*   **Naming:** Name widget objects in Qt Designer with a descriptive prefix (e.g., `btn_submit`, `txt_username`).

## Commits

*   Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.
