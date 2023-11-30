# git_tree.py

import os
import subprocess
from collections import defaultdict

# Define color codes for HTML output
ADDED_COLOR = 'style="color:green;"'   # Green for added files
DELETED_COLOR = 'style="color:red;"'   # Red for deleted files
MODIFIED_COLOR = 'style="color:purple;"' # Purple for modified files
UNCHANGED_COLOR = 'style="color:black;"' # Black for unchanged files

def tree():
    return defaultdict(tree)

def add_to_tree(base, path, status):
    parts = path.split('/', 1)
    if len(parts) == 1:
        base[parts[0]] = status
    else:
        add_to_tree(base[parts[0]], parts[1], status)

def is_directory_modified(subtree):
    if isinstance(subtree, dict):
        for item in subtree.values():
            if is_directory_modified(item):
                return True
    else:
        return subtree in ['A', 'D', 'M']
    return False

def print_tree_html(base, prefix='', include_unchanged=True):
    html_output = ''
    for i, (path, subtree) in enumerate(base.items()):
        dir_modified = is_directory_modified(subtree) if isinstance(subtree, dict) else False
        dir_color = MODIFIED_COLOR if dir_modified else UNCHANGED_COLOR

        if isinstance(subtree, dict):
            html_output += f"{prefix}{'└── ' if i == len(base) - 1 else '├── '}<span {dir_color}>{path}</span><br>"
            html_output += print_tree_html(subtree, prefix + ('    ' if i == len(base) - 1 else '│   '), include_unchanged)
        else:
            if subtree == 'U' and not include_unchanged:
                continue
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

def generate_html_comparison(repo_path, item1, item2, include_unchanged=True):
    file_list = compare_branches(repo_path, item1, item2)
    my_tree = tree()
    for status, path in file_list:
        if status == 'U' and not include_unchanged:
            continue
        add_to_tree(my_tree, path, status)
    return print_tree_html(my_tree, include_unchanged=include_unchanged)

generate_html_comparison('/Users/maddy/my_repos/repo_store/ccar_streamlit','246e6b2a','938162f1')