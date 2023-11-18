from flask import Flask, request, render_template,session
import utilities
import subprocess

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    sshAddress = ""
    selected_branch = ""
    branches = []
    depth=""
    tree_output=''
    folder_depth=''

    if request.method == "POST":
        sshAddress = request.form.get("sshAddress")
        selected_branch = request.form.get("selectedBranch")
        depth= request.form.get("depthValue")
        folder_depth= request.form.get("folderdepthValue")

        # If SSH address is provided, get branches
        if sshAddress:
            message = utilities.get_repo(sshAddress)
            branches = message.splitlines()  # Split the message into a list of branches


        # Check if repo name or branch has changed
        repo_changed = sshAddress != session.get('last_sshAddress')
        branch_changed = selected_branch != session.get('last_selected_branch')

        if selected_branch is not None:
            utilities.clone_repo(sshAddress,selected_branch,'/Users/maddy/my_repos/repo_store')
            session['last_sshAddress'] = sshAddress
            session['last_selected_branch'] = selected_branch

        if int(folder_depth)>0:
            raw_tree_output = subprocess.check_output(['tree','-L',str(folder_depth),
                                                        '/Users/maddy/my_repos/repo_store/pandas'], text=True)
                # Split the output into lines and remove the first line
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