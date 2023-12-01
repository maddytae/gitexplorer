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
END_COLOR = '\033[0m'

def tree():
    return defaultdict(tree)

def add_to_tree(base, path, status):
    parts = path.split('/', 1)
    if len(parts) == 1:
        base[parts[0]] = status
    else:
        node = base[parts[0]]
        if not isinstance(node, dict):
            node = base[parts[0]] = tree()  # Convert to dict if it was a leaf node
        add_to_tree(node, parts[1], status)

def is_directory_modified(subtree):
    if isinstance(subtree, dict):
        for value in subtree.values():
            if value in ['A', 'D', 'M'] or is_directory_modified(value):
                return True
    return subtree in ['A', 'D', 'M']

def print_tree(base, prefix='', only_modifications=False):
    for i, (path, subtree) in enumerate(base.items()):
        dir_modified = is_directory_modified(subtree) if isinstance(subtree, dict) else False
        dir_color = MODIFIED_COLOR if dir_modified else UNCHANGED_COLOR

        if isinstance(subtree, dict):
            if any(subtree.values()) or not only_modifications:
                print(f"{prefix}{'└── ' if i == len(base) - 1 else '├── '}{dir_color}{path}{END_COLOR}")
                print_tree(subtree, prefix + ('    ' if i == len(base) - 1 else '│   '), only_modifications)
        else:
            if subtree in ['A', 'D', 'M'] or not only_modifications:
                color = {
                    'A': ADDED_COLOR,
                    'D': DELETED_COLOR,
                    'M': MODIFIED_COLOR,
                    'U': UNCHANGED_COLOR
                }.get(subtree, UNCHANGED_COLOR)
                print(f"{prefix}{'└── ' if i == len(base) - 1 else '├── '}{color}{path}{END_COLOR}")

def compare_items(repo_path, item1, item2):
    # Build the git diff command with the full repository path
    diff_command = f"git -C {repo_path} diff --name-status {item1} {item2}"
    result = subprocess.run(diff_command, shell=True, capture_output=True, text=True)
    diff_output = result.stdout.splitlines()

    # Build the git ls-tree commands with the full repository path
    files_item1_command = f"git -C {repo_path} ls-tree -r --name-only {item1}"
    files_item2_command = f"git -C {repo_path} ls-tree -r --name-only {item2}"

    files_item1 = subprocess.run(files_item1_command, shell=True, capture_output=True, text=True).stdout.splitlines()
    files_item2 = subprocess.run(files_item2_command, shell=True, capture_output=True, text=True).stdout.splitlines()

    all_files = sorted(set(files_item1 + files_item2))

    file_statuses = {line.split('\t')[1]: line.split('\t')[0] for line in diff_output}
    return [(file_statuses.get(file, 'U'), file) for file in all_files]


def main():
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Usage: ./git_tree.py <path-to-repo> <item1> <item2> [--only-modifications]")
        sys.exit(1)

    repo_path, item1, item2 = sys.argv[1], sys.argv[2], sys.argv[3]
    only_modifications = '--only-modifications' in sys.argv

    file_list = compare_items(repo_path, item1, item2)

    my_tree = tree()
    for status, path in file_list:
        if status in ['A', 'D', 'M'] or not only_modifications:
            add_to_tree(my_tree, path, status)

    print_tree(my_tree, only_modifications=only_modifications)

if __name__ == "__main__":
    main()
