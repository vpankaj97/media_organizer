
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
                    file_path = file_path.split('.')[0] + '.mov'
                    filename = filename.split('.')[0] + '.mov'
                    shutil.move(file_path, os.path.join(
                        destination_folder, filename))


dates = '2022-04-05'
date_to_check = datetime.datetime.strptime(dates, '%Y-%m-%d').date()
folder = 'Pune - 2022 March - 18 Degrees'
root_path = r'E:\Images\Pankaj\Camera\toSync\2022'
categories = ["Images", "Videos", "Live Photos"]

for category in categories:
    print(f"Running for category: {category}")
    find_file_by_date(os.path.join(root_path, category),
                      date_to_check, category)


# Delete empty directories

try:
    cmd = f'ROBOCOPY {root_path} {root_path} /S /MOVE'
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, check=True)

except subprocess.CalledProcessError as e:
    # print(f"Error: {e}")
    pass
