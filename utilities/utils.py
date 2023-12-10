import os
import subprocess
import requests
import shutil
# import json
# from io import StringIO
# import pandas as pd

import settings
st = settings.PrepareSettings()

from .git_tree_cli import compare_items


def get_git_branches(repo_path):


    # Run the Git command
    command = ['git', '-C', repo_path, 'branch', '-r']
    result = subprocess.run(command, capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode != 0:
        print("Error running git command:", result.stderr)
        return []

    # Parse the output to extract branch names
    branches = []
    for line in result.stdout.splitlines():
        # Remove leading characters (*, space, remotes/origin/)
        # cleaned_line = line.replace('* ', '').replace('origin/', '').strip()
        cleaned_line = line.replace('* ', '').strip()

        # Skip the line if it's a pointer to another branch (e.g., HEAD -> origin/main)
        if ' -> ' in cleaned_line:
            continue

        branches.append(cleaned_line)

    return branches






def get_commits_for_branch(full_path, branch):
    

    # Run the Git command for the specified branch
    command = ['git', '-C', full_path, 'log', '--pretty=format:%H', branch]
    result = subprocess.run(command, capture_output=True, text=True)

    # Check if command execution was successful
    if result.returncode != 0:
        print("Error running git log:", result.stderr)
        return []

    # Parse the output to extract commit hashes and truncate them to 10 characters
    commits = [commit[:8] for commit in result.stdout.strip().split('\n')]
    return commits



def get_modified_files(repo_path, commit1, commit2):

    item1,item2=commit1,commit2
   
    file_list = compare_items(repo_path, item1, item2)

    modified_files=[]
    for status, path in file_list:
        if status in ['A', 'D', 'M']:
            modified_files.append(path)

    return modified_files

def get_unique_authors_for_branch(full_path, branch):

    # Run the Git command for the specified branch to get author names
    command = ['git', '-C', full_path, 'log', '--pretty=format:%an', branch]
    result = subprocess.run(command, capture_output=True, text=True)

    # Check if command execution was successful
    if result.returncode != 0:
        print("Error running git log:", result.stderr)
        return []

    # Extract author names from the output
    authors = result.stdout.strip().split('\n')

    # Get unique authors
    unique_authors = sorted(list(set(authors)), key=str.lower)

    return unique_authors

import subprocess

def get_commits(full_path, branch, author=None):

    # Initialize the base Git command
    command = ['git', '-C', full_path, 'log', '--pretty=format:%H', branch]

    # Add author filtering if author is provided
    if author:
        command.insert(-1, f'--author={author}')

    # Run the Git command
    result = subprocess.run(command, capture_output=True, text=True)

    # Check if command execution was successful
    if result.returncode != 0:
        print("Error running git log:", result.stderr)
        return []

    # Parse the output to extract commit hashes and truncate them to 8 characters
    commits = [commit[:8] for commit in result.stdout.strip().split('\n')]
    return commits

def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                # If you have subdirectories, you can use shutil.rmtree(file_path)
                pass  # Add logic here if you have subdirectories
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def process_paste(code, file_path):
    with open(file_path, 'w') as file:
        file.write(code)


#put this to yaml
def process_link(newInput, file_path, size):
    size_limit=size*1024*1024  # size is in mb and size_limit is translating it to byte.
    try:
        response = requests.get(newInput)
        response.raise_for_status()

        if len(response.content) < size_limit:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)

    except Exception as e:
        return f"An error occurred: {e}"



def process_upload(fileUpload, file_path):
    if fileUpload:
        try:
            fileUpload.save(file_path)
            return "File uploaded successfully."
        except Exception as e:
            return f"An error occurred: {e}"
    else:
        return "No file was uploaded."

def recreate_directory(directory_path):
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)  # Removes the directory even if it contains files/folders
    os.makedirs(directory_path, exist_ok=True) 