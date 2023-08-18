import os
import shutil
import argparse


def create_category_folders(root_dir):
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
    video_extensions = [".mp4", ".avi", ".mov", ".mkv", ".wmv"]

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)

            if any(file_path.lower().endswith(ext) for ext in image_extensions):
                category_folder = "Images"
            elif any(file_path.lower().endswith(ext) for ext in video_extensions):
                category_folder = "Videos"
            else:
                category_folder = "Unknown"

            source_dir = os.path.dirname(file_path)
            destination_dir = os.path.join(source_dir, category_folder)

            # Create the category folder if it doesn't exist
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)

            # Move the file to the category folder
            shutil.move(file_path, os.path.join(destination_dir, filename))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Categorize files in sub-directories based on type.")
    parser.add_argument("root_directory", help="Path to the root directory")
    args = parser.parse_args()

    root_directory = args.root_directory
    create_category_folders(root_directory)
