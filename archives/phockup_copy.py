import os
import shutil
import datetime
import argparse

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
    for root, _, files in os.walk(root_directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            minimum_date = get_minimum_date(file_path)
            if minimum_date is not None:
                year_folder = os.path.join(root_directory, str(minimum_date.year))
                destination_folder = os.path.join(year_folder, filename)

                if not os.path.exists(year_folder):
                    os.mkdir(year_folder)

                shutil.move(file_path, destination_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize files based on creation date.")
    parser.add_argument("root_directory", help="Root directory to start organizing files.")
    args = parser.parse_args()

    root_directory = args.root_directory
    organize_files_by_date(root_directory)

    #python script_name.py /path/to/your/root/directory

    # Delete empty directories
    try:
        import subprocess
        cmd = f'ROBOCOPY {root_directory} {root_directory} /S /MOVE'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        #print(f"Error: {e}")
        pass