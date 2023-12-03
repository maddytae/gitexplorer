import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import utilities as ut
import settings
import subprocess

import logging

logging.basicConfig(level=logging.DEBUG)

st = settings.PrepareSettings()

app = Flask(__name__)
app.secret_key = "khiadh2727sdhks888s"

@app.route("/", methods=["GET", "POST"])
def main():
    error_message = None
    if request.method == "POST":
        sshAddress = request.form.get("sshAddress")
        if sshAddress:
            try:
                ut.repo_cloning(sshAddress, ut.return_full_path(sshAddress), st.repo_size_limit)
                session["sshAddress"] = sshAddress
                repo_name = sshAddress.split('/')[-1].replace('.git', '')
                return redirect(url_for("repo", repo_name=repo_name))
            except ut.SizeLimitExceededError as e:
                error_message = "Repo exceeded size limit."
            except ut.InvalidSSHAddressError as e:
                error_message = "Invalid ssh address."
            except Exception as e:
                error_message = "An unexpected error occurred."

    return render_template("main.html", error_message=error_message)


@app.route("/repo/<repo_name>", methods=["GET", "POST"])
def repo(repo_name):
    sshAddress = session.get("sshAddress", "")
    branches = ut.get_git_branches(sshAddress) if sshAddress else []
    
    # Initialize variables with default values
    selected_branch1 = selected_branch2 = selected_commit1 = selected_commit2 = selected_filePath = ""
    commits1 = commits2 = filePaths = []

    if request.method == "POST":
        # Fetch the selected branches and commits from the form
        selected_branch1 = request.form.get("branch1", "")
        selected_branch2 = request.form.get("branch2", "")
        selected_commit1 = request.form.get("commit1", "")
        selected_commit2 = request.form.get("commit2", "")
        selected_filePath= request.form.get("filePath", "")

        # Fetch commits for the selected branches
        if selected_branch1:
            commits1 = ut.get_commits_for_branch(sshAddress, selected_branch1)

        if selected_branch2:
            commits2 = ut.get_commits_for_branch(sshAddress, selected_branch2)


        if selected_commit1 and selected_commit2:
            filePaths = ut.get_modified_files(sshAddress,selected_commit1,selected_commit2)
            diff_folder_path = os.path.join(app.static_folder, 'diff')
            ut.clear_directory(diff_folder_path)

            repo_path = os.path.join(st.repo_store, repo_name)

            output_path1 = os.path.join(app.static_folder, 'diff', 'folder_diff.html')
            output_path2 = os.path.join(app.static_folder, 'diff', 'folder_diff_modifications_only.html')

            # Command to run the git_tree_cli.py script
            command1 = f"python utilities/git_tree_cli.py {repo_path} {selected_commit1} {selected_commit2} | ansifilter --encoding=UTF-8 --html"
            command2 = f"python utilities/git_tree_cli.py {repo_path} {selected_commit1} {selected_commit2} --only-modifications | ansifilter --encoding=UTF-8 --html"

            # Running the command and writing the output to the HTML file
            with open(output_path1, 'w') as file:
                subprocess.run(command1, shell=True, stdout=file, check=True)
            with open(output_path2, 'w') as file:
                subprocess.run(command2, shell=True, stdout=file, check=True)


        if selected_commit1 and selected_commit2 and selected_filePath:

            subprocess.run(["git", "-C", repo_path, "checkout", selected_commit1, selected_filePath])
            subprocess.run(["git", "-C", repo_path, "checkout", selected_commit2, selected_filePath])

            output_path3 = os.path.join(app.static_folder, 'diff', 'line.html')
            output_path4 = os.path.join(app.static_folder, 'diff', 'no_line.html')
            output_path5 = os.path.join(app.static_folder, 'diff', 'side_by_side.html')
            
            command3 = f"git -C {repo_path} diff -U10000 {selected_commit1} {selected_commit2} {selected_filePath} |delta --line-numbers | ansifilter --encoding=UTF-8 --html"
            command4 = f"git -C {repo_path} diff -U10000 {selected_commit1} {selected_commit2} {selected_filePath}|delta  | ansifilter --encoding=UTF-8 --html"
            command5 = f"git -C {repo_path} diff -U10000 {selected_commit1} {selected_commit2} {selected_filePath}|delta --width=150 --side-by-side | ansifilter --encoding=UTF-8 --html"
  
            with open(output_path3, 'w') as file:
                subprocess.run(command3, shell=True, stdout=file, check=True)
            with open(output_path4, 'w') as file:
                subprocess.run(command4, shell=True, stdout=file, check=True)
            with open(output_path5, 'w') as file:
                subprocess.run(command5, shell=True, stdout=file, check=True)


    return render_template("repo.html", repo_name=repo_name, 
                           branches=branches, 
                           filePaths=filePaths,
                           selected_filePath=selected_filePath,
                           commits1=commits1, 
                           commits2=commits2, 
                           selected_branch1=selected_branch1,
                           selected_branch2=selected_branch2,
                           selected_commit1=selected_commit1,
                           selected_commit2=selected_commit2)

if __name__ == "__main__":
    app.run(debug=True)




