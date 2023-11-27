from flask import Flask, render_template, request,session
import os
import subprocess
import utilities as ut

import settings
st=settings.PrepareSettings()

app = Flask(__name__)
app.secret_key = 'khiadh2727sdhks888s'

@app.route('/', methods=['GET'])
def index():
 
    return render_template('index.html')

@app.route('/generate_diff', methods=['POST'])
def generate_diff():

    sshAddress=''


    # Get the SSH address from the form
    sshAddress = request.form.get('sshAddress', '')


 
    # Perform the git clone operation using the imported function
    if sshAddress:
        try:
            ut.repo_cloning(sshAddress, ut.return_full_path(sshAddress), st.repo_size_limit)
            message = "Repository successfully cloned."
        except Exception as e:
            message = f"Failed to clone repository. Error: {str(e)}"




    # branches=[]

    # Get the form data
    branch1 = request.form.get('branch1')
    branch2 = request.form.get('branch2')
    commit1 = request.form.get('commit1')
    commit2 = request.form.get('commit2')
    sshAddress = request.form.get('sshAddress')


    # branches=ut.get_git_branches(sshAddress)
    # print(branches)

    branches=['fd','fs','edf']


    # files_ready = False

    # Path to the static directory
    static_folder = app.static_folder

    # Logic to generate new sets of HTML files based on the selections
    if branch1 == 'a' and branch2 == 'b' and commit1 == 'x' and commit2 == 'y':
        # files_ready = True
        # Load the content of the HTML files from static directory
        with open(os.path.join(static_folder, 'diff/line.html'), 'r') as file:
            line_html = file.read()
        with open(os.path.join(static_folder, 'diff/no_line.html'), 'r') as file:
            no_line_html = file.read()
        with open(os.path.join(static_folder, 'diff/side_by_side.html'), 'r') as file:
            side_by_side_html = file.read()
    else:
        line_html, no_line_html, side_by_side_html = '', '', ''

    # Render the template with the form data and the HTML content
    return render_template('index.html', 
                           branch1=branch1, 
                           branch2=branch2, 
                           commit1=commit1, 
                           commit2=commit2, 
                           line_html=line_html, 
                           no_line_html=no_line_html, 
                           side_by_side_html=side_by_side_html,
                           sshAddress=sshAddress,
                           branches=branches,
                           message=message)

if __name__ == '__main__':
    app.run(debug=True)


