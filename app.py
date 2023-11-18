from flask import Flask, request, render_template, session
import utilities
import subprocess
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

@app.route("/", methods=["GET", "POST"])
def home():
    sshAddress = ""
    selected_branch = ""
    branches = []
    depth = ""
    tree_output = ''
    folder_depth = ''

    if request.method == "POST":
        sshAddress = request.form.get("sshAddress")
        selected_branch = request.form.get("selectedBranch")
        depth = request.form.get("depthValue")
        folder_depth = request.form.get("folderdepthValue")

        if sshAddress:
            message = utilities.get_repo(sshAddress)
            branches = message.splitlines()

        repo_changed = sshAddress != session.get('last_sshAddress')
        branch_changed = selected_branch != session.get('last_selected_branch')

        clone_directory = '/Users/maddy/my_repos/repo_store'
        repo_name = sshAddress.split('/')[-1].replace('.git', '')
        repo_path = os.path.join(clone_directory, repo_name)

        if selected_branch and (repo_changed or branch_changed):
            utilities.clone_repo(sshAddress, selected_branch, clone_directory)
            session['last_sshAddress'] = sshAddress
            session['last_selected_branch'] = selected_branch

        if folder_depth and os.path.exists(repo_path):
            folder_depth = int(folder_depth)
            if folder_depth > 0:
                raw_tree_output = subprocess.check_output(['tree', '-L', str(folder_depth), repo_path], text=True)
                lines = raw_tree_output.split('\n')
                tree_output = '\n'.join(lines[1:])  

    return render_template('index.html', branches=branches, 
                           sshAddress=sshAddress,
                           selected_branch=selected_branch,
                           depth=depth,
                           tree_output=tree_output,
                           folder_depth=folder_depth)

if __name__ == "__main__":
    app.run(debug=True)
