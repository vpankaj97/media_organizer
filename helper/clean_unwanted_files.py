import argparse
import os
import subprocess

UNWANTED_FILES = [
                  '.outside',
                  '.inside',
                  '.picasa.ini',
                  'Thumbs.db'
               ]


def remove_unwanted_files (root_dir):
   for dirpath, _, filenames in os.walk(root_dir):
      for filename in filenames:
         file_path = os.path.join(dirpath, filename)

         if filename in UNWANTED_FILES:
            os.remove(file_path)

if __name__ == "__main__":
   parser = argparse.ArgumentParser(
      description="Categorize files in sub-directories based on type.")
   parser.add_argument("root_directory", help="Path to the root directory")
   args = parser.parse_args()

   root_directory = args.root_directory
   remove_unwanted_files(root_directory)

   # Delete empty directories
   try:
      cmd = f"""ROBOCOPY "{root_directory}" "{root_directory}" /S /MOVE"""
      print(f"""Cleaning up empty folder - Command: | {cmd}""")
      result = subprocess.run(
         cmd, shell=True, capture_output=True, text=True, check=True)

   except subprocess.CalledProcessError as e:
      # print(f"Error: {e}")
      pass
