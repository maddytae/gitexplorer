# git_tree.py

import os
import subprocess
from collections import defaultdict

# Define color codes for HTML output
ADDED_COLOR = 'style="color:green;"'   # Green for added files
DELETED_COLOR = 'style="color:red;"'   # Red for deleted files
MODIFIED_COLOR = 'style="color:purple;"' # Brown for modified files
UNCHANGED_COLOR = 'style="color:black;"' # Black for unchanged files
DIR_COLOR = 'style="color:blue;"'     # Blue for directories

def tree():
    return defaultdict(tree)

def add_to_tree(base, path, status):
    parts = path.split('/', 1)
    if len(parts) == 1:
        base[parts[0]] = status
    else:
        add_to_tree(base[parts[0]], parts[1], status)

def print_tree_html(base, prefix=''):
    html_output = ''
    for i, (path, subtree) in enumerate(base.items()):
        if isinstance(subtree, dict):
            html_output += f"{prefix}{'└── ' if i == len(base) - 1 else '├── '}<span {DIR_COLOR}>{path}</span><br>"
            html_output += print_tree_html(subtree, prefix + ('    ' if i == len(base) - 1 else '│   '))
        else:
            color = {
                'A': ADDED_COLOR,
                'D': DELETED_COLOR,
                'M': MODIFIED_COLOR,
                'U': UNCHANGED_COLOR
            }.get(subtree, UNCHANGED_COLOR)
            html_output += f"{prefix}{'└── ' if i == len(base) - 1 else '├── '}<span {color}>{path}</span><br>"
    return html_output

def compare_branches(repo_path, item1, item2):
    os.chdir(repo_path)
    diff_command = f"git diff --name-status {item1} {item2}"
    result = subprocess.run(diff_command, shell=True, capture_output=True, text=True)
    diff_output = result.stdout.splitlines()

    files_item1 = subprocess.run(f"git ls-tree -r --name-only {item1}", shell=True, capture_output=True, text=True).stdout.splitlines()
    files_item2 = subprocess.run(f"git ls-tree -r --name-only {item2}", shell=True, capture_output=True, text=True).stdout.splitlines()

    all_files = sorted(set(files_item1 + files_item2))

    file_statuses = {line.split('\t')[1]: line.split('\t')[0] for line in diff_output}
    return [(file_statuses.get(file, 'U'), file) for file in all_files]

def generate_html_comparison(repo_path, item1, item2):
    file_list = compare_branches(repo_path, item1, item2)
    my_tree = tree()
    for status, path in file_list:
        add_to_tree(my_tree, path, status)
    return print_tree_html(my_tree)
