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
    selected_branch1 = selected_branch2 = selected_commit1 = selected_commit2 = ""
    commits1 = commits2 = []

    if request.method == "POST":
        # Fetch the selected branches and commits from the form
        selected_branch1 = request.form.get("branch1", "")
        selected_branch2 = request.form.get("branch2", "")
        selected_commit1 = request.form.get("commit1", "")
        selected_commit2 = request.form.get("commit2", "")

        # Fetch commits for the selected branches
        if selected_branch1:
            commits1 = ut.get_commits_for_branch(sshAddress, selected_branch1)
        if selected_branch2:
            commits2 = ut.get_commits_for_branch(sshAddress, selected_branch2)

        # # Log for debugging
        # app.logger.debug(f"Selected Branch 1: {selected_branch1}, Selected Branch 2: {selected_branch2}")
        # app.logger.debug(f"Selected Commit 1: {selected_commit1}, Selected Commit 2: {selected_commit2}")

        # Generate HTML comparison when both commits are selected
        if selected_commit1 and selected_commit2:
            repo_path = os.path.join(st.repo_store, repo_name)
            html_comparison = ut.generate_html_comparison(repo_path, selected_commit1, selected_commit2,include_unchanged=True)

            # Save the HTML content to a file
            output_path = os.path.join(app.static_folder, 'diff', 'folder_diff.html')
            with open(output_path, 'w') as file:
                file.write(html_comparison)



    return render_template("repo.html", repo_name=repo_name, 
                           branches=branches, 
                           commits1=commits1, 
                           commits2=commits2, 
                           selected_branch1=selected_branch1,
                           selected_branch2=selected_branch2,
                           selected_commit1=selected_commit1,
                           selected_commit2=selected_commit2)

if __name__ == "__main__":
    app.run(debug=True)




