import argparse
import json
import os
from src.catalog import get_images, update_rating, get_pick_status, get_last_modified

def execute_command(args):
    catalog_path = args.catalog_path
    last_checked_file = os.path.join(os.path.dirname(catalog_path), ".photon_last_checked")

    if args.command == "list":
        images = get_images(catalog_path)
        if images:
            filtered_images = []
            for img in images:
                # img structure: id, fileName, relativePath, absolutePath, rating, pick
                img_rating = img[4]
                img_pick = img[5]

                # Apply rating filter
                if args.rating is not None and img_rating != args.rating:
                    continue

                # Apply flag filter
                if args.flag == "picked" and img_pick != 1:
                    continue
                elif args.flag == "rejected" and img_pick != 2:
                    continue
                elif args.flag == "unflagged" and img_pick != 0:
                    continue

                filtered_images.append(img)

            if not filtered_images:
                print("No images found matching the criteria.")
                return

            print(f"Found {len(filtered_images)} images matching the criteria:")
            for img in filtered_images:
                print(
                    f"  ID: {img[0]}, File: {img[1]}, Rating: {img[4]}, Pick: {img[5]}"
                )
    elif args.command == "rate":
        update_rating(catalog_path, args.image_id, args.rating)
    elif args.command == "export":
        images = get_pick_status(catalog_path)
        if images:
            kept_images = [img[0] for img in images if img[1] == 1]
            rejected_images = [img[0] for img in images if img[1] == 0]

            output_data = {
                "kept": kept_images,
                "rejected": rejected_images
            }

            output_file = os.path.join(args.output_dir, "session-summary.json")
            with open(output_file, "w") as f:
                json.dump(output_data, f, indent=4)
            print(f"Exported session summary to {output_file}")
    elif args.command == "check-changes":
        current_modified = get_last_modified(catalog_path)
        last_checked_modified = None

        if os.path.exists(last_checked_file):
            with open(last_checked_file, "r") as f:
                try:
                    last_checked_modified = float(f.read())
                except ValueError:
                    pass  # Ignore if file content is invalid

        if current_modified:
            if last_checked_modified is None or current_modified != last_checked_modified:
                print(f"Catalog has changed. Last modified: {current_modified}")
                with open(last_checked_file, "w") as f:
                    f.write(str(current_modified))
            else:
                print("Catalog has not changed.")
        else:
            print("Could not determine catalog modification time.")

def run_cli(cli_args=None):
    parser = argparse.ArgumentParser(
        description="A headless CLI for interacting with Lightroom catalogs."
    )
    parser.add_argument("catalog_path", help="The path to the Lightroom catalog file (*.lrcat).")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # 'list' command
    list_parser = subparsers.add_parser("list", help="List all images in the catalog.")
    list_parser.add_argument("--rating", type=int, choices=range(0, 6), help="Filter images by star rating (0-5).")
    list_parser.add_argument("--flag", choices=["picked", "rejected", "unflagged"], help="Filter images by pick flag status.")

    # 'rate' command
    rate_parser = subparsers.add_parser("rate", help="Set the rating for a specific image.")
    rate_parser.add_argument("image_id", type=int, help="The local ID of the image to rate.")
    rate_parser.add_argument("rating", type=int, choices=range(0, 6), help="The rating to set (0-5).")

    # 'export' command
    export_parser = subparsers.add_parser("export", help="Export kept and rejected image lists.")
    export_parser.add_argument("--output-dir", default=".", help="The directory to save the export files to.")

    # 'check-changes' command
    check_changes_parser = subparsers.add_parser("check-changes", help="Check the catalog for external changes.")

    args = parser.parse_args(cli_args)

if __name__ == "__main__":
    run_cli()