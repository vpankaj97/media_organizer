import os
import shutil
import argparse
import subprocess

def move_files_to_main_folders(root_dir):
    # Create main folders if they don't exist
    main_folders = ['Images', 'Videos', 'Others']
    for folder in main_folders:
        folder_path = os.path.join(root_dir, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    # Traverse through all subdirectories
    for root, _, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1].lower()

            # Move files to the respective main folders
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
                shutil.move(file_path, os.path.join(root_dir, 'Images', file))
            elif file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
                shutil.move(file_path, os.path.join(root_dir, 'Videos', file))
            else:
                shutil.move(file_path, os.path.join(root_dir, 'Others', file))

    # Delete empty directories
    try:
        cmd = 'ROBOCOPY . . /S /MOVE'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()  # Get the command output as a string
    except subprocess.CalledProcessError as e:
        #print(f"Error: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Organize photos, videos, and other files into separate folders.')
    parser.add_argument('root_directory_path', type=str, help='Path to the root directory containing subdirectories.')

    args = parser.parse_args()
    root_directory_path = args.root_directory_path

    if not os.path.exists(root_directory_path):
        print("Error: The specified root directory does not exist.")
    else:
        move_files_to_main_folders(root_directory_path)
