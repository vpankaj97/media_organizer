from difPy import dif
import argparse
import os

parser = argparse.ArgumentParser(
    description="Categorize files in sub-directories based on type.")
parser.add_argument("-r", "--root_directory",
                    help="Path to the root directory")
args = parser.parse_args()

directory = args.root_directory

# create a difPy search object
search = dif(directory)

# get the results
duplicates = search.result

# print the results
for key, value in duplicates.items():
    print(f"Image: {value['location']}")
    for match_key, match_value in value['matches'].items():
        print(f"Duplicate: {match_value['location']}")
