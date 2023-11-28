import os
import subprocess
import settings
st = settings.PrepareSettings()


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
        cleaned_line = line.replace('* ', '').replace('origin/', '').strip()

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

def get_commits_of_branch(sshAddress, branch):
    full_path = return_full_path(sshAddress)

    # Run the Git command for the specified branch
    command = ['git', '-C', full_path, 'log', '--pretty=format:%H', branch]
    result = subprocess.run(command, capture_output=True, text=True)

    # Check if command execution was successful
    if result.returncode != 0:
        print("Error running git log:", result.stderr)
        return []

    # Parse the output to extract commit hashes
    commits = result.stdout.strip().split('\n')
    return commits

