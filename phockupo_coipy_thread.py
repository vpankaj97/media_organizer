import os
import shutil
import datetime
import concurrent.futures

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
    def move_file(file_path, destination_folder):
        shutil.move(file_path, destination_folder)

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

                    futures.append(executor.submit(move_file, file_path, destination_folder))

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error moving file: {e}")

if __name__ == "__main__":
    root_directory = r"E:\Images\Pankaj\Camera"  # Replace this with your actual root directory path
    organize_files_by_date(root_directory)