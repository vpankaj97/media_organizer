
import subprocess
import os
import shutil
import datetime
from PIL import Image, ExifTags


def get_minimum_date(file_path):
    try:
        stat = os.stat(file_path)
        creation_time = stat.st_ctime
        access_time = stat.st_atime
        modified_time = stat.st_mtime

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
        return None


def find_file_by_date(root_directory, date_to_check, category):
    for sub, _, files in os.walk(root_directory):
        for filename in files:

            # print(f"Looking at file: {filename} - {sub}")

            file_path = os.path.join(sub, filename)
            minimum_date = get_minimum_date(file_path)

            if minimum_date == date_to_check:

                print(f"Found file: {filename} - {sub}")

                if os.path.basename(sub) == folder:
                    # file already at the required folder
                    continue

                if not os.path.exists(os.path.join(root_directory, folder)):
                    os.mkdir(os.path.join(root_directory, folder))

                destination_folder = os.path.join(root_directory, folder)
                print(f"Moving to {destination_folder}")

                shutil.move(file_path, os.path.join(
                    destination_folder, filename))

                if category == 'Live Photos':
                    # Check for mov
                    file_path = file_path.split('.')[0]+'.mov'
                    print(f"Moving {file_path} to {destination_folder}")
                    if os.path.exists(file_path):
                        filename = filename.split('.')[0] + '.mov'
                        try:
                            shutil.move(file_path, os.path.join(destination_folder, filename))
                        except FileNotFoundError:
                            file_path = file_path.split('.')[0]+'.MOV'
                            shutil.move(file_path, os.path.join(destination_folder, filename))


date = '28'
month = '05'
year = '2023'
final_date = f"{year}-{month}-{date}"
date_to_check = datetime.datetime.strptime(final_date, '%Y-%m-%d').date()
folder = "Rishu Bday 2023"
root_paths = [
    r'G:\Images\Rishu\Camera\2023'
]
categories = ["Images", "Videos", "Live Photos"]

for root_path in root_paths:

    print(f"Searching for files in Path: {root_path}")

    for category in categories:
        print(f"Running for category: {category}")
        find_file_by_date(os.path.join(root_path, category),
                          date_to_check, category)

    # Delete empty directories
    try:
        cmd = f'ROBOCOPY "{root_path}" "{root_path}" /S /MOVE'
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=True)

    except subprocess.CalledProcessError as e:
        # print(f"Error: {e}")
        pass
