import os
import shutil
import argparse
import multiprocessing

def categorize_file(file_path, image_extensions, video_extensions):
    print(f"To categorise {file_path.lower()}", end = " | ")
    
    
    if file_path.lower().endswith(tuple(image_extensions)):
        category_folder = "Images"
    elif file_path.lower().endswith(tuple(video_extensions)):
        category_folder = "Videos"
    else:
        category_folder = "Unknown"

    source_dir = os.path.dirname(file_path)
    destination_dir = os.path.join(source_dir, category_folder)

    if os.path.basename(os.path.abspath(source_dir)) in ['Images','Videos','Unknown']:
        print("Skipped!!")
        return
    # Create the category folder if it doesn't exist
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Move the file to the category folder
    
    shutil.move(file_path, os.path.join(destination_dir, os.path.basename(file_path)))
    print("Moved!!")
    #Exmpla phockup log - [2023-07-20 17:30:47] - [INFO] - E:\Images\Rishu\Camera\2022\05-May\Images\IMG_9336.JPG => E:\Images\Rishu\Camera\2022\IMG_9336.JPG

def process_files_in_directory(directory, image_extensions, video_extensions):
    for entry in os.scandir(directory):
        if entry.is_file():
            categorize_file(entry.path, image_extensions, video_extensions)

def create_category_folders(root_dir):
    image_extensions = {".jpg", ".jpeg", ".heic"}
    video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}

    num_cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_cores)

    for dirpath, _, _ in os.walk(root_dir):
        pool.apply_async(process_files_in_directory, args=(dirpath, image_extensions, video_extensions))

    pool.close()
    pool.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Categorize files in sub-directories based on type.")
    parser.add_argument("root_directory", help="Path to the root directory")
    args = parser.parse_args()

    root_directory = args.root_directory
    create_category_folders(root_directory)

    # Delete empty directories
    try:
        import subprocess
        cmd = 'ROBOCOPY . . /S /MOVE'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        #print(f"Error: {e}")
        pass

#run python "D:\fast_organizer.py" "E:\Images\Family\toModify"
#phockup - python phockup.py -m -o -d "YYYY" "E:\Images\Rishu\Camera\2016" "E:\Images\Rishu\Camera\2016"