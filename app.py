import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import utilities as ut
import settings

st = settings.PrepareSettings()

app = Flask(__name__)
app.secret_key = "khiadh2727sdhks888s"

@app.route("/", methods=["GET", "POST"])
def index():
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

    return render_template("index.html", error_message=error_message)



@app.route("/repo/<repo_name>", methods=["GET", "POST"])
def repo(repo_name):
    sshAddress = session.get("sshAddress", "")
    branches = ut.get_git_branches(sshAddress) if sshAddress else []

    branch1 = []
    branch2 = []
    commits1 = []
    commits2 = []



    if request.method == "POST":
        branch1 = request.form.get("branch1")
        branch2 = request.form.get("branch2")

        if branch1:
            commits1 = ut.get_commits_for_branch(branch1)
        if branch2:
            commits2 = ut.get_commits_for_branch(branch2)

    return render_template("repo.html", repo_name=repo_name, branches=branches, commits1=commits1, commits2=commits2, selected_branch1=branch1, selected_branch2=branch2)


if __name__ == "__main__":
    app.run(debug=True)
