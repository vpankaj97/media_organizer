Syntax:

`python "D:\Windows\Portable Apps\Organizer\file_organizer.py" -r "<folder_path>" -d [True/False/Empty] -m [True/False/Empty] -mf -rm`

1. Default run: Creates basic categories and moves files into those categories.

    `python "D:\Windows\Portable Apps\Organizer\file_organizer.py" -r "<folder_path>"`

2. Force Reset a Full folder:

    `python "D:\Windows\Portable Apps\Organizer\file_organizer.py" -r "G:\Images\Rishu\Camera\2020" -mf`

    * Make sure to pass only a SINGLE DIRECORY that needs base level categories made!!!
    * It will wipe out any sub-directory you have!!

3. Group of Base Level directories:

    `python "D:\Windows\Portable Apps\Organizer\file_organizer.py" -r "G:\Images\Rishu\Camera\2020" -m`

    * Root directory passed contains actual directories that need categories themselves.
    * Basically works the same as a full reset but at level 1 of sub-directories.

4. Date Wise Forced Categorisation [UNREVERSIBLE]

    `python "D:\Windows\Portable Apps\Organizer\file_organizer.py" -r "G:\Images\Rishu\Camera" -d`


where:
 1. -r -> root_path
 2. -d -> date_wise
 3. -m -> move on basis of sub-root
 4. -mf -> move to root
 5. -rm -> Removes unwanted files

[DEBUG]
To run:

Plan - two ways

1. To get base folders - better way to adopt move by date function - YYYY/[category]
2. To catrgorise inside folders - Look through all files in sub-directories and pull data into Category folders in root - [sub-directory]/[category]

Move files by specific date - requiremtn - frst sort by years and then run
