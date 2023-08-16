# %% [markdown]
# # Better way to do this

# %%
import os
import shutil
import datetime
import concurrent.futures
import argparse

# %%
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".heic",".JPG", ".JPEG", ".HEIC")
VIDEO_EXTENSIONS = (".mp4", ".avi", ".mkv", ".mov", ".wmv",".MP4", ".AVI", ".MKV", ".MOV", ".WMV")

# %%
def get_minimum_date(file_path):
    try:
        stat = os.stat(file_path)
        creation_time = stat.st_ctime
        access_time = stat.st_atime
        modified_time = stat.st_mtime

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

    shutil.move(file_path, os.path.join(media_type_folder, os.path.basename(file_path)))


# %%
def handle_live_photos(folder_path):
    images_folder = os.path.join(folder_path, "Images")
    videos_folder = os.path.join(folder_path, "Videos")
    live_photos_folder = os.path.join(folder_path, "Live Photos")

    for image_file in os.listdir(images_folder):
        if os.path.splitext(image_file)[0] + ".MOV" in os.listdir(videos_folder):
            image_path = os.path.join(images_folder, image_file)
            video_path = os.path.join(videos_folder, os.path.splitext(image_file)[0] + ".MOV")

            if not os.path.exists(live_photos_folder):
                os.mkdir(live_photos_folder)

            shutil.move(image_path, os.path.join(live_photos_folder, image_file))
            shutil.move(video_path, os.path.join(live_photos_folder, os.path.basename(video_path)))


# %%
def organize_files_by_date(root_directory):

    #Move files into Categories
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for root, _, files in os.walk(root_directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                minimum_date = get_minimum_date(file_path)
                if minimum_date is not None:
                    year_folder = os.path.join(root_directory, str(minimum_date.year))

                    if not os.path.exists(year_folder):
                        os.mkdir(year_folder)

                    futures.append(executor.submit(move_and_categorize, file_path, year_folder))

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error moving and categorizing file: {e}")

    # Handle Live Photos
    for root, dirs, _ in os.walk(root_directory):
        for dir_name in dirs:
            folder_path = os.path.join(root_directory, dir_name)
            try:

                handle_live_photos(folder_path)
            except Exception:
                pass


# %%
def create_category_folders(root_dir):
    image_extensions = [".jpg", ".jpeg", ".heic"]
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

            if os.path.basename(os.path.abspath(source_dir)) in ['Images','Videos','Unknown']:
                # print("Skipped!!")
                continue
            
            destination_dir = os.path.join(source_dir, category_folder)

            # Create the category folder if it doesn't exist
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)

            # Move the file to the category folder
            shutil.move(file_path, os.path.join(destination_dir, filename))

# %%
date_wise = False

if __name__ == "__main__":

    
    parser = argparse.ArgumentParser(description='Organize photos, videos, and other files into separate folders.')
    parser.add_argument('root_directory_path', type=str, help='Path to the root directory containing subdirectories.')

    args = parser.parse_args()
    root_directory = args.root_directory_path

    if not os.path.exists(root_directory):
        print("Error: The specified root directory does not exist.")

    # %%
    if date_wise:
        organize_files_by_date(root_directory) # Only for Camera - where we want to organize by date
    else:
        create_category_folders(root_directory) # for normal organizing


    # Delete empty directories
    import subprocess

    try:
        cmd = f'ROBOCOPY {root_directory} {root_directory} /S /MOVE'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)

    except subprocess.CalledProcessError as e:
        #print(f"Error: {e}")
        pass
