#!/usr/bin/env python3

## this creates tree for any directory and doesnot utilize git in any way
# "-T" Skip hidden files/directories if hide_dotfiles is True
#Usage ./tree_script.py <path-to-directory>

import os
import sys

# Define color codes
FILE_COLOR = '\033[30m'  # Black for files
DIR_COLOR = '\033[94m'  # Blue for directories
END_COLOR = '\033[0m'

def generate_tree(directory, hide_dotfiles=False, prefix=''):
    if prefix == '':  # only print the root on the first call
        print(DIR_COLOR + directory + END_COLOR)

    files = sorted(os.listdir(directory))
    for index, file in enumerate(files):
        if hide_dotfiles and file.startswith('.'):
            continue  # Skip hidden files/directories if hide_dotfiles is True

        path = os.path.join(directory, file)
        if os.path.isdir(path):
            colored_path = DIR_COLOR + file + END_COLOR
            print(prefix + '├── ' + colored_path)
            generate_tree(path, hide_dotfiles, prefix + '│   ' if index != len(files) - 1 else prefix + '    ')
        else:
            colored_path = FILE_COLOR + file + END_COLOR
            connector = '└── ' if index == len(files) - 1 else '├── '
            print(prefix + connector + colored_path)

def main():
    hide_dotfiles = '-T' in sys.argv
    directory = sys.argv[-1]  # Assuming the last argument is the directory
    generate_tree(directory, hide_dotfiles)

if __name__ == "__main__":
    main()
