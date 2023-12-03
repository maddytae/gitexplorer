import os
import subprocess
import settings
st = settings.PrepareSettings()

from .git_tree_cli import compare_items


def get_git_branches(sshAddress):

    repo_path = return_full_path(sshAddress)

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


def return_full_path(sshAddress):
    repo_name = sshAddress.split('/')[-1].replace('.git', '')
    # full_clone_path = os.path.join('/Users/maddy/my_repos/repo_store', repo_name)
    full_clone_path = os.path.join(st.repo_store, repo_name)

    
    return full_clone_path



def get_commits_for_branch(sshAddress, branch):
    full_path = return_full_path(sshAddress)

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



def get_modified_files(sshAddress, commit1, commit2):


    repo_path = return_full_path(sshAddress)
    item1,item2=commit1,commit2
   
    file_list = compare_items(repo_path, item1, item2)

    modified_files=[]
    for status, path in file_list:
        if status in ['A', 'D', 'M']:
            modified_files.append(path)

    return modified_files


###Note that it won't return same result as git log --all --format='%H' | sort -u | wc -l            
###because not all commits may be associate with branches; there might be commits that are there whose branch might have 
### been deleted but commit hash are still reachable.
def get_commit_dataframes_by_branch(repo_path):
    # Get all branches
    branch_command = ["git", "-C", repo_path, "branch", "-r", "--format=%(refname:short)"]
    branch_result = subprocess.run(branch_command, capture_output=True, text=True)
    if branch_result.returncode != 0:
        raise Exception(f"Error getting branches: {branch_result.stderr}")

    branches = branch_result.stdout.strip().split('\n')

    # Initialize a dictionary to hold branch names as keys and DataFrames as values
    branch_dataframes = {}

    for branch in branches:
        # Get commit details for each branch
        commit_command = ["git", "-C", repo_path, "log", "--pretty=format:%H|%an|%ae|%ad", "--date=iso", branch]
        commit_result = subprocess.run(commit_command, capture_output=True, text=True)
        if commit_result.returncode != 0:
            raise Exception(f"Error getting commits for branch {branch}: {commit_result.stderr}")

        # Collecting commit data for the branch
        commit_data = []
        for line in commit_result.stdout.strip().split('\n'):
            commit_hash, author, email, date = line.split('|')
            commit_data.append({'Commit': commit_hash, 'Author': author, 'Email': email, 'Date': date})

        # Create DataFrame for the current branch and add it to the dictionary
        branch_df = pd.DataFrame(commit_data)
        branch_dataframes[branch.strip()] = branch_df

    return branch_dataframes

