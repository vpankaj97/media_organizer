# %% [markdown]
# # Better way to do this

# %%
import subprocess
import argparse
import os
import shutil
import datetime
import concurrent.futures
from PIL import Image, ExifTags

# %%
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".heic", ".JPG", ".JPEG", ".HEIC")
VIDEO_EXTENSIONS = (".mp4", ".avi", ".mkv", ".mov", ".wmv",
                    ".MP4", ".AVI", ".MKV", ".MOV", ".WMV")

# %%


def get_minimum_date(file_path):
    try:
        stat = os.stat(file_path)
        creation_time = stat.st_ctime
        access_time = stat.st_atime
        modified_time = stat.st_mtime
        dt = datetime.datetime.fromtimestamp(
            min(creation_time, access_time, modified_time)).date()
        # print(dt)

        try:

            img = Image.open(file_path)
            img_exif = img.getexif()

            for key, val in img_exif.items():
                if key == 306:
                    dt = val[:10]
                    dt = datetime.datetime.strptime(dt, '%Y:%m:%d').date()
                    # print(dt)
                    break

            return dt

        except Exception as err:
            return datetime.datetime.fromtimestamp(min(creation_time, access_time, modified_time)).date()

    except OSError as e:
        print(f"Error getting minimum date for {file_path}: {e}")
        return None


# %%
def move_and_categorize(file_path, folder_path):
    _, ext = os.path.splitext(file_path)

    if ext.lower() in IMAGE_EXTENSIONS:
        media_type_folder = os.path.join(folder_path, "Images")
    elif ext.lower() in VIDEO_EXTENSIONS:
        media_type_folder = os.path.join(folder_path, "Videos")
    else:
        media_type_folder = os.path.join(folder_path, "Others")

    if not os.path.exists(media_type_folder):
        os.mkdir(media_type_folder)

    shutil.move(file_path, os.path.join(
        media_type_folder, os.path.basename(file_path)))


# %%
def handle_live_photos(folder_path):
    images_folder = os.path.join(folder_path, "Images")
    videos_folder = os.path.join(folder_path, "Videos")
    live_photos_folder = os.path.join(folder_path, "Live Photos")

    for image_file in os.listdir(images_folder):
        if os.path.splitext(image_file)[0] + ".MOV" in os.listdir(videos_folder):
            image_path = os.path.join(images_folder, image_file)
            video_path = os.path.join(
                videos_folder, os.path.splitext(image_file)[0] + ".MOV")

            if not os.path.exists(live_photos_folder):
                os.mkdir(live_photos_folder)

            shutil.move(image_path, os.path.join(
                live_photos_folder, image_file))
            shutil.move(video_path, os.path.join(
                live_photos_folder, os.path.basename(video_path)))


# %%
def organize_files_by_date(root_directory):

    # Move files into Categories
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for root, _, files in os.walk(root_directory):
            print(f"Working on Files in Directory: {root}")
            for filename in files:
                file_path = os.path.join(root, filename)
                minimum_date = get_minimum_date(file_path)
                if minimum_date is not None:
                    year_folder = os.path.join(
                        root_directory, str(minimum_date.year))

                    if not os.path.exists(year_folder):
                        os.mkdir(year_folder)

                    futures.append(executor.submit(
                        move_and_categorize, file_path, year_folder))

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error moving and categorizing file: {e}")


# %%
def create_category_folders(root_dir):
    try:

        image_extensions = [".jpg", ".jpeg", ".heic"]
        video_extensions = [".mp4", ".avi", ".mov", ".mkv", ".wmv"]

        for dirpath, _, filenames in os.walk(root_dir):
            print(f"Working on Files in Directory: {dirpath}")
            for filename in filenames:

                try:
                    file_path = os.path.join(dirpath, filename)

                    if any(file_path.lower().endswith(ext) for ext in image_extensions):
                        category_folder = "Images"
                    elif any(file_path.lower().endswith(ext) for ext in video_extensions):
                        category_folder = "Videos"
                    else:
                        category_folder = "Unknown"

                    source_dir = os.path.dirname(file_path)

                    if os.path.basename(os.path.abspath(source_dir)) in ['Images', 'Videos', 'Unknown']:
                        # print("Skipped!!")
                        continue

                    destination_dir = os.path.join(source_dir, category_folder)

                    # Create the category folder if it doesn't exist
                    if not os.path.exists(destination_dir):
                        os.makedirs(destination_dir)

                    # Move the file to the category folder
                    shutil.move(file_path, os.path.join(
                        destination_dir, filename))

                except Exception as e:
                    print(e)
                    continue

    except PermissionError as p_err:
        print(p_err)
        return "Failed"

# %%


def move_files_to_main_folders(root_dir):
    try:
        # Create main folders if they don't exist
        main_folders = ['Images', 'Videos', 'Others']
        for folder in main_folders:
            folder_path = os.path.join(root_dir, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

        # Traverse through all subdirectories
        for root, _, files in os.walk(root_dir):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    file_extension = os.path.splitext(file)[1].lower()

                    # Move files to the respective main folders
                    if file_extension in ['.jpg', '.jpeg', '.heic']:
                        shutil.move(file_path, os.path.join(
                            root_dir, 'Images', file))
                    elif file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
                        shutil.move(file_path, os.path.join(
                            root_dir, 'Videos', file))
                    else:
                        shutil.move(file_path, os.path.join(
                            root_dir, 'Others', file))
                except Exception as e:
                    print(e)
                    continue
    except PermissionError as p_err:
        print(p_err)
        return "Failed"


# %%
parser = argparse.ArgumentParser(
    description="Categorize files in sub-directories based on type.")
parser.add_argument("-r", "--root_directory",
                    help="Path to the root directory")
parser.add_argument("-d", "--date_wise", action='store_true', help="Path to the root directory")
parser.add_argument("-m", "--move_to_root", action='store_true', help="Path to the root directory")
args = parser.parse_args()

date_wise = bool(args.date_wise)
move_to_root = bool(args.move_to_root)
root_directory = args.root_directory

print(
    f"\nRunning for {root_directory} \n\twith Args - Date_wise: {date_wise} and move_to_root: {move_to_root}")

# %%
# Run categorisation
if date_wise:
    # Only for Camera - where we want to organize by date
    organize_files_by_date(root_directory)

elif move_to_root:
    # Create categories in base directly
    move_files_to_main_folders(root_directory)

else:
    create_category_folders(root_directory)  # for normal organizing

# Handle Live Photos
for root, dirs, _ in os.walk(root_directory):
    for dir_name in dirs:
        folder_path = os.path.join(root_directory, dir_name)
        try:

            handle_live_photos(folder_path)
        except Exception:
            pass


# Delete empty directories

try:
    cmd = f"""ROBOCOPY "{root_directory}" "{root_directory}" /S /MOVE"""
    print(f"""Cleaning up empty folder - Command: | {cmd}""")
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, check=True)

except subprocess.CalledProcessError as e:
    # print(f"Error: {e}")
    pass
