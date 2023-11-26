#!/usr/bin/env python3

import os
import subprocess
import sys
from collections import defaultdict

# Define color codes
ADDED_COLOR = '\033[32m'   # Green for added files
DELETED_COLOR = '\033[31m' # Red for deleted files
MODIFIED_COLOR = '\033[33m' # Brown for modified files
UNCHANGED_COLOR = '\033[30m' # Black for unchanged files
DIR_COLOR = '\033[94m'     # Blue for directories
END_COLOR = '\033[0m'

def tree():
    """Create a factory function for a tree-like data structure."""
    return defaultdict(tree)

def add_to_tree(base, path, status):
    """Recursively add paths to the tree data structure."""
    parts = path.split('/', 1)
    if len(parts) == 1:
        base[parts[0]] = status
    else:
        add_to_tree(base[parts[0]], parts[1], status)

def print_tree(base, prefix=''):
    """Recursively print the tree data structure."""
    for i, (path, subtree) in enumerate(base.items()):
        if isinstance(subtree, dict):
            print(f"{prefix}{'└── ' if i == len(base) - 1 else '├── '}{DIR_COLOR}{path}{END_COLOR}")
            print_tree(subtree, prefix + ('    ' if i == len(base) - 1 else '│   '))
        else:
            color = {
                'A': ADDED_COLOR,
                'D': DELETED_COLOR,
                'M': MODIFIED_COLOR,
                'U': UNCHANGED_COLOR
            }.get(subtree, UNCHANGED_COLOR)
            print(f"{prefix}{'└── ' if i == len(base) - 1 else '├── '}{color}{path}{END_COLOR}")

def compare_branches(repo_path, item1, item2):
    """Compare two branches or two commits  and return a list of (status, file_path) tuples."""
    os.chdir(repo_path)
    diff_command = f"git diff --name-status {item1} {item2}"

    
    result = subprocess.run(diff_command, shell=True, capture_output=True, text=True)
    diff_output = result.stdout.splitlines()

    # Get a list of all files in both branches
    files_item1 = subprocess.run(f"git ls-tree -r --name-only {item1}", shell=True, capture_output=True, text=True).stdout.splitlines()
    files_item2 = subprocess.run(f"git ls-tree -r --name-only {item2}", shell=True, capture_output=True, text=True).stdout.splitlines()

    # Combine lists and sort uniquely
    all_files = sorted(set(files_item1 + files_item2))

    file_statuses = {line.split('\t')[1]: line.split('\t')[0] for line in diff_output}
    return [(file_statuses.get(file, 'U'), file) for file in all_files]

def main():
    if len(sys.argv) != 4:
        print("Usage: ./git_tree.py <path-to-repo> <item1> <item2>")
        sys.exit(1)

    repo_path, item1, item2 = sys.argv[1], sys.argv[2], sys.argv[3]
    file_list = compare_branches(repo_path, item1, item2)

    my_tree = tree()
    for status, path in file_list:
        add_to_tree(my_tree, path, status)

    print_tree(my_tree)

if __name__ == "__main__":
    main()
