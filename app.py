from flask import Flask, request, render_template
import utilities

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    sshAddress = ""
    selected_branch = ""
    branches = []
    depth=""

    if request.method == "POST":
        sshAddress = request.form.get("sshAddress")
        selected_branch = request.form.get("selectedBranch")
        depth= request.form.get("depthValue")

        # If SSH address is provided, get branches
        if sshAddress:
            message = utilities.get_repo(sshAddress)
            branches = message.splitlines()  # Split the message into a list of branches

        print("Selected Branch:", selected_branch)
        print("Selected Depth:", depth)

    return render_template('index.html', branches=branches, 
                           sshAddress=sshAddress,
                           selected_branch=selected_branch,
                           depth=depth)

if __name__ == "__main__":
    app.run(debug=True)
