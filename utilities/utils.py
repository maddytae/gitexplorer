import os
import subprocess

def get_repo(sshAddress):
    try:
        # Use subprocess.check_output to capture the command's output
        result = subprocess.check_output(["git", "ls-remote", "--heads", sshAddress], text=True)

        # Process the output to extract branch names
        branches = []
        for line in result.splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1].startswith('refs/heads/'):
                branch_name = parts[1].split('/')[-1]  # Extract the branch name
                branches.append(branch_name)

        return '\n'.join(branches)  # Join branch names into a single string
    except subprocess.CalledProcessError as e:
        # Handle errors in command execution
        return str(e)

