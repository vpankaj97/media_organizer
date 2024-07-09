""" Module for File Organizer """

import os

from helper.func import (
    parse_args,
    move_files_to_main_folders,
    handle_live_photos,
    delete_empty_dirs,
    organize_files_by_date,
    create_category_folders,
)

if __name__ == "__main__":
    root_directory, date_wise, move, test, remove_flag, move_to_root = parse_args()

    print(
        f"""\nRunning for {root_directory} 
        with Args - Date_wise: {date_wise}, Move: {move} and test: {test}"""
    )

    if date_wise:
        # Only for Camera - where we want to organize by date
        organize_files_by_date(root_directory, test)

    elif move:
        for root, subdr, _ in os.walk(root_directory):
            try:
                if root == root_directory:
                    for subdir in subdr:
                        path = os.path.join(root_directory, subdir)
                        move_files_to_main_folders(path, test, remove_flag)
                        handle_live_photos(path, test, remove_flag)
            except:
                pass

    elif move_to_root:
        move_files_to_main_folders(root_directory, test, remove_flag)
        handle_live_photos(root_directory, test, remove_flag)

    else:
        # Create categories in every folder which is NOT Images, Videos and Others.
        create_category_folders(root_directory, test, remove_flag)

    delete_empty_dirs(root_directory, test, remove_flag)
