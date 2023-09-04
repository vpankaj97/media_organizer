from PIL import Image, ExifTags
import os
import datetime
import argparse
import pathlib
import subprocess

IGNORED_DIR = ['Live Photos']
UNWANTED_FILES = [
                  '.outside',
                  '.inside',
                  '.picasa.ini',
                  'Thumbs.db'
               ]

IMAGE_EXTENSIONS = (".JPG", ".JPEG", ".HEIC", ".PNG")
VIDEO_EXTENSIONS = (".MP4", ".AVI", ".MKV", ".MOV",
                    ".WMV", ".MTS", ".3GP", ".MPG")


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
                    dt = val
                    dt = datetime.datetime.strptime(dt, '%Y:%m:%d %H:%M:%S%f')

                    # print(dt)
                    break

            return dt

        except Exception as err:
            # print(err)
            dt = datetime.datetime.fromtimestamp(
                min(creation_time, access_time, modified_time))

            return dt

    except OSError as e:
        print(f"Error getting minimum date for {file_path}: {e}")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Categorize files in sub-directories based on type.")
    parser.add_argument("root_directory", help="Path to the root directory")
    args = parser.parse_args()

    root_directory = args.root_directory

    for root, _, files in os.walk(root_directory):
        print(f"Working on Files in Directory: {root}")

        folder = os.path.basename(root)

        if folder in IGNORED_DIR:
            print(f"Skipping - {folder}")
            continue

        retry_count = 0

        for filename in sorted(files):

            # print(filename)

            prefix = ""

            file_extension = pathlib.Path(filename).suffix
            file_path = os.path.join(root, filename)

            if file_extension.upper() in IMAGE_EXTENSIONS:
                prefix = "IMG"
            elif file_extension.upper() in VIDEO_EXTENSIONS:
                prefix = "VID"
            else:
                if filename in UNWANTED_FILES:
                    print(f"Removing file - {filename}")
                    os.remove(file_path)
                else:
                    print(f"Skipping file - {filename}")
                continue

            minimum_date = get_minimum_date(file_path)

            new_filename = f"""{prefix}_{minimum_date.strftime('%Y%m%d_%H%M%S')}{str(minimum_date.microsecond)[:1]}{file_extension}"""
            # print(new_filename)
            new_file_path = os.path.join(root, new_filename)

            if filename == new_filename:
               continue

            try:
                os.rename(file_path, new_file_path)

                #reset count
                retry_count = 0

            except Exception as e:

                try:
                    retry_count += 1

                    new_filename = f"""{prefix}_{minimum_date.strftime('%Y%m%d_%H%M%S')}{str(minimum_date.microsecond)[:1]}_{retry_count:02}{file_extension}"""
                    # print(new_filename)
                    new_file_path = os.path.join(root, new_filename)

                    os.rename(file_path, new_file_path)
                except Exception as e:
                    #  print(e)
                    continue

    # Delete empty directories
    try:
        cmd = f'ROBOCOPY "{root_directory}" "{root_directory}" /S /MOVE'
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=True)

    except subprocess.CalledProcessError as e:
        # print(f"Error: {e}")
        pass
