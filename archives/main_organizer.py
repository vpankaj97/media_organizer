import os
import shutil
import datetime
import argparse
import concurrent.futures

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".heic")
VIDEO_EXTENSIONS = (".mp4", ".avi", ".mkv", ".mov", ".wmv")

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


def organize_files_by_date(root_directory):
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

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for root, _, files in os.walk(root_directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                minimum_date = get_minimum_date(file_path)
                if minimum_date is not None:
                    year_folder = os.path.join(root_directory, str(minimum_date.year))
                    destination_folder = os.path.join(year_folder, filename)

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize files based on creation date.")
    parser.add_argument("root_directory", help="Root directory to start organizing files.")
    args = parser.parse_args()

    root_directory = args.root_directory
    organize_files_by_date(root_directory)

    # Delete empty directories
    import subprocess

    try:
        cmd = f'ROBOCOPY {root_directory} {root_directory} /S /MOVE'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)

    except subprocess.CalledProcessError as e:
        #print(f"Error: {e}")
        pass
