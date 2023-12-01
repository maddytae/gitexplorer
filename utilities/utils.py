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
    
    """
    Returns a list of modified files between two commits in a given repository.
    :param repo_path: Path to the repository
    :param commit1: The first commit hash
    :param commit2: The second commit hash
    :return: List of modified files
    """

    repo_path = return_full_path(sshAddress)

    try:
        # Running the git diff command to find modified files between two commits
        result = subprocess.run(
            ["git", "-C", repo_path, "diff", "--name-only", commit1, commit2],
            capture_output=True, text=True, check=True
        )
        # Splitting the output by new lines to get individual file paths
        modified_files = result.stdout.splitlines()
        return modified_files
    except subprocess.CalledProcessError as e:
        # In case of error, return the error message
        return f"Error occurred: {e}"


