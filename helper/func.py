""" Functions for File Organizer """

import os
import shutil
import datetime
import concurrent.futures
from typing import Optional
import subprocess
import argparse
from PIL import Image


from helper.config import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, RAW_EXTENSIONS
from helper.config import UNWANTED_FILES


def parse_args():
    """Parses Args"""
    parser = argparse.ArgumentParser(
        description="Categorize files in sub-directories based on type."
    )
    parser.add_argument("-r", "--root_directory", help="Path to the root directory")
    parser.add_argument(
        "-d", "--date_wise", action="store_true", help="Flag to group by date"
    )
    parser.add_argument(
        "-m",
        "--move",
        action="store_true",
        help="Flag to Move all files to root of the 1st Subdirectory",
    )
    parser.add_argument(
        "-mf",
        "--move_to_root",
        action="store_true",
        help="Flag to Move all files to root",
    )
    parser.add_argument("-t", "--test", action="store_true", help="Enable to only test")
    parser.add_argument(
        "-rm",
        "--remove",
        action="store_true",
        help="Remove '.' files and empty folders",
    )

    args = parser.parse_args()
    return (
        args.root_directory,
        bool(args.date_wise),
        bool(args.move),
        bool(args.test),
        bool(args.remove),
        bool(args.move_to_root),
    )


def delete_empty_dirs(root_dir, test_run, rm) -> None:
    """Remove Empty Folders"""
    # Delete empty directories
    try:
        cmd = f"""ROBOCOPY "{root_dir}" "{root_dir}" /S /MOVE"""
        # print(f"""Cleaning up empty folder - Command: | {cmd}""")
        if not test_run:
            subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        pass

    if rm:
        # Delete files starting with a dot
        for root, _, files in os.walk(root_dir):
            for filename in files:
                try:
                    if filename.startswith(".") or filename in UNWANTED_FILES:
                        file_path = os.path.join(root, filename)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            # print(f"Deleted file: {file_path}")
                        else:
                            print(f"Path - {file_path} does not exist")

                except PermissionError:
                    continue


def get_minimum_date(my_file_path: str) -> Optional[datetime.datetime]:
    """Gets minimum date from Image"""
    try:
        stat = os.stat(my_file_path)
        creation_time = stat.st_ctime
        access_time = stat.st_atime
        modified_time = stat.st_mtime
        dt = datetime.datetime.fromtimestamp(
            min(creation_time, access_time, modified_time)
        ).date()

        try:

            img = Image.open(my_file_path)
            img_exif = img.getexif()

            for key, val in img_exif.items():
                if key == 306:
                    dt = val[:10]
                    dt = datetime.datetime.strptime(dt, "%Y:%m:%d").date()
                    break

            return dt

        except Exception:
            return datetime.datetime.fromtimestamp(
                min(creation_time, access_time, modified_time)
            ).date()

    except OSError as e:
        print(f"Error getting minimum date for {my_file_path}: {e}")
        return None


def move_and_categorize(file_path, folder_path):
    """Moves and Catgorizes files"""

    _, ext = os.path.splitext(file_path)

    if ext.upper() in IMAGE_EXTENSIONS:
        media_type_folder = os.path.join(folder_path, "Images")
    elif ext.upper() in VIDEO_EXTENSIONS:
        media_type_folder = os.path.join(folder_path, "Videos")
    elif ext.upper() in RAW_EXTENSIONS:
        media_type_folder = os.path.join(folder_path, "RAW")
    else:
        media_type_folder = os.path.join(folder_path, "Others")

    if not os.path.exists(media_type_folder):
        os.mkdir(media_type_folder)

    shutil.move(file_path, os.path.join(media_type_folder, os.path.basename(file_path)))


def handle_live_photos(folder_path, test, rm):
    """Handles Live Photos"""
    images_folder = os.path.join(folder_path, "Images")
    videos_folder = os.path.join(folder_path, "Videos")
    live_photos_folder = os.path.join(folder_path, "Live Photos")
    live_photos = os.path.join(live_photos_folder, "Images")
    live_videos = os.path.join(live_photos_folder, "Videos")

    os.makedirs(live_photos_folder, exist_ok=True)
    os.makedirs(live_photos, exist_ok=True)
    os.makedirs(live_videos, exist_ok=True)

    video_file_names = [
        os.path.splitext(video_file)[0] for video_file in os.listdir(videos_folder)
    ]

    for image_file in os.listdir(images_folder):
        try:

            image_file_name = os.path.splitext(image_file)[0]

            if image_file_name in video_file_names:
                image_path = os.path.join(images_folder, image_file)
                video_path = os.path.join(videos_folder, image_file_name + ".MOV")

                if not os.path.exists(video_path):
                    print(f"Video File: {video_path} not found")
                    continue

                if os.path.basename(os.path.abspath(folder_path)) in ["Live Photos"]:
                    print(f"Already in Live Photos Folder: {folder_path}")
                    return

                shutil.move(image_path, os.path.join(live_photos, image_file))
                shutil.move(
                    video_path, os.path.join(live_videos, os.path.basename(video_path))
                )
                if test:
                    print("Breaking")
                    break
        except Exception as e:
            print(e)
            continue


def organize_files_by_date(root_directory, test):
    """Organizes file by Date"""

    # Move files into Categories
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for root, _, files in os.walk(root_directory):
            print(f"Working on Files in Directory: {root}")
            for filename in files:
                file_path = os.path.join(root, filename)
                minimum_date = get_minimum_date(file_path)
                if minimum_date is not None:
                    year_folder = os.path.join(root_directory, str(minimum_date.year))

                    if not os.path.exists(year_folder):
                        os.mkdir(year_folder)

                    futures.append(
                        executor.submit(move_and_categorize, file_path, year_folder)
                    )

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error moving and categorizing file: {e}")


def move_files_to_main_folders(root_dir, test, rm):
    """Move files to main folders"""
    try:
        # Create main folders if they don't exist
        main_folders = ["Images", "Videos", "Others", "RAW"]
        for folder in main_folders:
            folder_path = os.path.join(root_dir, folder)
            if not os.path.exists(folder_path) and not test:
                os.makedirs(folder_path)

        # Traverse through all subdirectories
        for root, _, files in os.walk(root_dir):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    file_extension = os.path.splitext(file)[1].upper()

                    # Move files to the respective main folders
                    if not test:
                        if file_extension in IMAGE_EXTENSIONS:
                            shutil.move(
                                file_path, os.path.join(root_dir, "Images", file)
                            )
                        elif file_extension in VIDEO_EXTENSIONS:
                            shutil.move(
                                file_path, os.path.join(root_dir, "Videos", file)
                            )

                        elif file_extension in RAW_EXTENSIONS:
                            shutil.move(file_path, os.path.join(root_dir, "RAW", file))

                        else:
                            shutil.move(
                                file_path, os.path.join(root_dir, "Others", file)
                            )
                except Exception as err:
                    print(err)
                    continue

        delete_empty_dirs(root_dir, test, rm)

    except PermissionError as p_err:
        print(p_err)
        return "Failed"


def create_category_folders(root_dir, test, rm):
    " Create Default categories in each folder you see in the Root Directory " ""
    try:

        for dirpath, _, filenames in os.walk(root_dir):
            print(f"Working on Files in Directory: {dirpath}")
            for filename in filenames:

                try:
                    file_path = os.path.join(dirpath, filename)

                    if any(file_path.upper().endswith(ext) for ext in IMAGE_EXTENSIONS):
                        category_folder = "Images"
                    elif any(
                        file_path.upper().endswith(ext) for ext in VIDEO_EXTENSIONS
                    ):
                        category_folder = "Videos"
                    elif any(file_path.upper().endswith(ext) for ext in RAW_EXTENSIONS):
                        category_folder = "RAW"
                    else:
                        category_folder = "Unknown"

                    source_dir = os.path.dirname(file_path)

                    if os.path.basename(os.path.abspath(source_dir)) in [
                        "Images",
                        "Videos",
                        "Unknown",
                    ]:
                        # print("Skipped!!")
                        continue

                    destination_dir = os.path.join(source_dir, category_folder)

                    # Create the category folder if it doesn't exist
                    if not os.path.exists(destination_dir):
                        os.makedirs(destination_dir)

                    # Move the file to the category folder
                    shutil.move(file_path, os.path.join(destination_dir, filename))

                except Exception as e:
                    print(e)
                    continue

    except PermissionError as p_err:
        print(p_err)
        return "Failed"
