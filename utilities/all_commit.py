import subprocess
import pandas as pd

def get_commit_dataframe_old(repo_path):
    # Define the git log command
    command = ["git", "-C", repo_path, "log", "--all", "--pretty=format:%H|%an|%ae|%ad", "--date=iso"]

    # Run the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)

    # Check for errors
    if result.returncode != 0:
        raise Exception(f"Error: {result.stderr}")

    # Split the output into lines and then into columns
    lines = result.stdout.strip().split('\n')
    data = [line.split('|') for line in lines]

    # Create a DataFrame
    df = pd.DataFrame(data, columns=['Commit', 'Author', 'Email', 'Date'])
    

    return df

def get_commit_dataframe(repo_path):
    # Get all branches
    branch_command = ["git", "-C", repo_path, "branch", "-r", "--format=%(refname:short)"]
    branch_result = subprocess.run(branch_command, capture_output=True, text=True)
    if branch_result.returncode != 0:
        raise Exception(f"Error getting branches: {branch_result.stderr}")

    branches = branch_result.stdout.strip().split('\n')

    # Collecting commit data
    commit_data = []
    for branch in branches:
        # Get commit details for each branch
        commit_command = ["git", "-C", repo_path, "log", "--all","--pretty=format:%H|%an|%ae|%ad", "--date=iso", branch]
        commit_result = subprocess.run(commit_command, capture_output=True, text=True)
        if commit_result.returncode != 0:
            raise Exception(f"Error getting commits for branch {branch}: {commit_result.stderr}")

        for line in commit_result.stdout.strip().split('\n'):
            commit_hash, author, email, date = line.split('|')
            commit_data.append({'Commit': commit_hash, 'Author': author, 'Email': email, 'Date': date, 'Branch': branch})

    # Create DataFrame from list
    df = pd.DataFrame(commit_data)
    df = df.groupby(['Commit', 'Author', 'Email', 'Date'])['Branch'].apply(';'.join).reset_index()



    return df

repo_path = '/Users/maddy/my_repos/repo_store/pandas'
df = get_commit_dataframe(repo_path)
df.to_csv('all.csv',index=False)
