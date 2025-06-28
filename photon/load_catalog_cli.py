import sys
import asyncio
import os
from photon.catalog_reader import LightroomCatalogReader
from typing import Optional


async def main(catalog_path: Optional[str] = None) -> None:
    if len(sys.argv) < 2:
        print("Usage: python load_catalog_cli.py <catalog_path>")
        sys.exit(1)

    catalog_path = sys.argv[1]
    reader = LightroomCatalogReader()

    if not os.path.exists(catalog_path):
        print(f"Error: Catalog not found at {catalog_path}")
        sys.exit(1)

    try:
        catalog = await reader.load_catalog_async(catalog_path)
        print(
            f"Successfully loaded catalog: {catalog.name} with {catalog.total_photo_count} photos and {catalog.total_folder_count} folders."
        )
        sys.exit(0)
    except Exception as e:
        print(f"Error loading catalog: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
