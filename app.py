import os
from flask import Flask, render_template, request, session, redirect, url_for,send_from_directory
import utilities as ut
import settings
import subprocess
import uuid
import shutil
import time
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

import logging

logging.basicConfig(level=logging.DEBUG)

st = settings.PrepareSettings()

app = Flask(__name__)
app.secret_key = "khiadh2727sdhks888s"



def clean_old_directories(base_path=st.repo_store, age_threshold_hours=1):
    current_time = time.time()
    age_threshold_seconds = age_threshold_hours * 3600

    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)

        if os.path.isdir(folder_path):
            last_modified = os.path.getmtime(folder_path)

            if current_time - last_modified > age_threshold_seconds:
                try:
                    print(f"Deleting folder: {folder_path}")
                    shutil.rmtree(folder_path)
                except Exception as e:
                    print(f"Error deleting {folder_path}: {e}")

# Initialize scheduler; clean up every 15 seconds for any folder that is more than 1 hour old
scheduler = BackgroundScheduler()
scheduler.add_job(func=clean_old_directories, trigger="interval", hours=0.25)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route("/", methods=["GET", "POST"])
def main():
    error_message = None

    if request.method == "POST":
        # Generate a unique session identifier
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())

        session_dir = os.path.join(st.repo_store, f"{session['session_id']}")
        main_diff_dir=os.path.join(session_dir,"main_diff_path")
        print(main_diff_dir)
        session['session_dir'] = session_dir
        session['main_diff_dir'] = main_diff_dir
        if not os.path.exists(session_dir):
            os.makedirs(session_dir, exist_ok=True)
        if not os.path.exists(main_diff_dir):
            os.makedirs(main_diff_dir, exist_ok=True)

        if 'sshAddress' in request.form:
            sshAddress = request.form.get("sshAddress")
            session["sshAddress"] = sshAddress
            if sshAddress:
                repo_name = sshAddress.split('/')[-1].replace('.git', '')
                # Set paths for repo and diff
                repo_path = os.path.join(session_dir, repo_name)
                diff_path = os.path.join(session_dir, 'diff')

                # Store paths in session
                session['repo_path'] = repo_path
                session['diff_path'] = diff_path

                try:
                    ut.repo_cloning(sshAddress, repo_path, st.repo_size_limit)
                    return redirect(url_for("repo", repo_name=repo_name))
                except ut.SizeLimitExceededError as e:
                    error_message = "Repo exceeded size limit."
                except ut.InvalidSSHAddressError as e:
                    error_message = "Invalid SSH address."
                except Exception as e:
                    error_message = f"An unexpected error occurred: {e}"
                    logging.error(f"Error: {e}", exc_info=True)

        # Check if CodeMirror text area form is submitted
        elif 'code1' in request.form and 'code2' in request.form:


            code1 = request.form["code1"]
            code2 = request.form["code2"]


            filename1='code1.txt'
            filename2='code2.txt'

            try:
                with open(os.path.join(main_diff_dir, filename1), 'w') as file:
                    file.write(code1)
                with open(os.path.join(main_diff_dir, filename2), 'w') as file:
                    file.write(code2)
            except Exception as e:
                error_message = f"An error occurred while saving files: {e}"
                logging.error(f"Error: {e}", exc_info=True)

            return redirect(url_for('main'))

    return render_template("main.html", error_message=error_message)


@app.route("/repo/<repo_name>", methods=["GET", "POST"])
def repo(repo_name):

    repo_path=session.get('repo_path', '')
    diff_path=session.get('diff_path','')
    os.makedirs(repo_path,exist_ok=True)
    os.makedirs(diff_path,exist_ok=True)


    branches = ut.get_git_branches(repo_path) if repo_path else []
    
    # Initialize variables with default values
    selected_branch1 = selected_branch2 = selected_commit1 = selected_commit2 = selected_filePath = ""
    selected_author1=selected_author2=""
    commits1 = commits2 = filePaths = authors1 = authors2=[]


    if request.method == "POST":
        # Fetch the selected branches and commits from the form
        selected_branch1 = request.form.get("branch1", "")
        selected_branch2 = request.form.get("branch2", "")
        selected_commit1 = request.form.get("commit1", "")
        selected_commit2 = request.form.get("commit2", "")
        selected_author1 = request.form.get("author1", "")
        selected_author2 = request.form.get("author2", "")
        selected_filePath= request.form.get("filePath", "")

        # Fetch authors for the selected branches
        if selected_branch1:
            authors1 = ut.get_unique_authors_for_branch(repo_path, selected_branch1)

        if selected_branch2:
            authors2 = ut.get_unique_authors_for_branch(repo_path, selected_branch2)

        # Fetch commits for the selected authors
        if selected_author1:
            commits1 = ut.get_commits(repo_path, selected_branch1,selected_author1)

        if selected_branch2:
            commits2 = ut.get_commits(repo_path, selected_branch2,selected_author2)

        if selected_commit1 and selected_commit2:
            filePaths = ut.get_modified_files(repo_path,selected_commit1,selected_commit2)

            output_path1 = os.path.join(diff_path, 'folder_diff.html')
            output_path2 = os.path.join(diff_path, 'folder_diff_modifications_only.html')

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

            output_path3 = os.path.join(diff_path, 'line.html')
            output_path4 = os.path.join(diff_path, 'no_line.html')
            output_path5 = os.path.join(diff_path, 'side_by_side.html')
            
            command3 = f"git -C {repo_path} diff -U10000 {selected_commit1} {selected_commit2} {selected_filePath} |delta --line-numbers | ansifilter --encoding=UTF-8 --html"
            command4 = f"git -C {repo_path} diff -U10000 {selected_commit1} {selected_commit2} {selected_filePath}|delta  | ansifilter --encoding=UTF-8 --html"
            command5 = f"git -C {repo_path} diff -U10000 {selected_commit1} {selected_commit2} {selected_filePath}|delta --width=150 --side-by-side | ansifilter --encoding=UTF-8 --html"
  
            with open(output_path3, 'w') as file:
                subprocess.run(command3, shell=True, stdout=file, check=True)
            with open(output_path4, 'w') as file:
                subprocess.run(command4, shell=True, stdout=file, check=True)
            with open(output_path5, 'w') as file:
                subprocess.run(command5, shell=True, stdout=file, check=True)


    diff_files = {
        'folder_diff': url_for('serve_diffs', filename='folder_diff.html', session_id=session['session_id']),
        'folder_diff_mod': url_for('serve_diffs', filename='folder_diff_modifications_only.html', session_id=session['session_id']),
        'line_diff': url_for('serve_diffs', filename='line.html', session_id=session['session_id']),
        'no_line_diff': url_for('serve_diffs', filename='no_line.html', session_id=session['session_id']),
        'side_by_side_diff': url_for('serve_diffs', filename='side_by_side.html', session_id=session['session_id'])
    }

    return render_template("repo.html", repo_name=repo_name, 
                           branches=branches, 
                           filePaths=filePaths,
                           selected_filePath=selected_filePath,
                           commits1=commits1, 
                           commits2=commits2, 
                           authors1=authors1,
                           authors2=authors2,
                           selected_author1=selected_author1,
                           selected_author2=selected_author2,
                           selected_branch1=selected_branch1,
                           selected_branch2=selected_branch2,
                           selected_commit1=selected_commit1,
                           selected_commit2=selected_commit2,
                           diff_files=diff_files)




@app.route("/diffs/<session_id>/<path:filename>")
def serve_diffs(session_id, filename):
    # Construct the full path to the file
    diff_path =session.get('diff_path', '')
    return send_from_directory(diff_path, filename)




if __name__ == "__main__":
    app.run(debug=True)




