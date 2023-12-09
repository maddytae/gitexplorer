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

# Shut down the scheduler w
# hen exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route("/", methods=["GET", "POST"])
def main():
    error_message = None
    show_checkbox_page = False
    diff_files = {}
    code1 = ''
    code2 = '' 
    newInput1 = ''
    newInput2 = ''
    uname1 = ''  # Initialize from session
    uname2 = ''  # Initialize from session


    if request.method == "POST":

        # Generate a unique session identifier
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())

        session_dir = os.path.join(st.repo_store, f"{session['session_id']}")
        main_diff_dir=os.path.join(session_dir,"main_diff_path")
   
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
        elif (any(request.form.get(key) for key in ['code1', 'newInput1']) or 
            'fileUpload1' in request.files) and \
            (any(request.form.get(key) for key in ['code2', 'newInput2']) or 
            'fileUpload2' in request.files):
            show_checkbox_page = True
            filename1='file1.txt'
            filename2='file2.txt'

            file_path1=os.path.join(main_diff_dir, 'file1.txt')
            file_path2=os.path.join(main_diff_dir, 'file2.txt')

            for v in ['code1', 'newInput1', 'fileUpload1']:
                if v == 'code1' and request.form.get('code1'):
                    code1 = ''
                    newInput1 = ''
                    fileUpload1 = None
                    code1 = request.form["code1"]
                    ut.process_paste(code1,file_path1)
                    break
                elif v == 'newInput1' and request.form.get('newInput1'):
                    # Logic for newInput1
                    code1 = ''
                    newInput1 = ''
                    fileUpload1 = None
                    newInput1=request.form["newInput1"]
                    ut.process_link(newInput1,file_path1) # this should save file1.txt in the destination folder
                    break

                elif v == 'fileUpload1' and 'fileUpload1' in request.files:
                    code1 = ''
                    newInput1 = ''
                    fileUpload1 = None
                    fileUpload1=request.files["fileUpload1"]
                    session['uname1'] = fileUpload1.filename
                    fileUpload1.save(file_path1)  #later see we can save in original file format
                    uname1 = session.get('uname1', '')


            for v in ['code2', 'newInput2', 'fileUpload2']:
                if v == 'code2' and request.form.get('code2'):
                    code2 = ''
                    newInput2 = ''
                    fileUpload2 = None
                    code2 = request.form["code2"]
                    ut.process_paste(code2,file_path2)
                    break
                elif v == 'newInput2' and request.form.get('newInput2'):
                    code2 = ''
                    newInput2 = ''
                    fileUpload2 = None
                    newInput2=request.form["newInput2"]
                    ut.process_link(newInput2,file_path2)
                    break
                elif v == 'fileUpload2' and 'fileUpload2' in request.files:
                    code2 = ''
                    newInput2 = ''
                    fileUpload2 = None
                    fileUpload2=request.files["fileUpload2"]
                    session['uname2'] = fileUpload2.filename
                    fileUpload2.save(file_path2)
                    uname2 = session.get('uname2', '')

                    # ut.process_upload(fileUpload2,file_path2)


            output_path1 = os.path.join(main_diff_dir, 'line.html')
            output_path2 = os.path.join(main_diff_dir, 'no_line.html')
            output_path3 = os.path.join(main_diff_dir, 'side_by_side.html')

            command1 = f"git -C {main_diff_dir} diff -U10000 {filename1} {filename2}  |delta --line-numbers | ansifilter --encoding=UTF-8 --html"
            command2 = f"git -C {main_diff_dir} diff -U10000 {filename1} {filename2}  |delta  | ansifilter --encoding=UTF-8 --html"
            command3 = f"git -C {main_diff_dir} diff -U10000 {filename1} {filename2}  |delta --width=150 --side-by-side | ansifilter --encoding=UTF-8 --html"
  
            with open(output_path1, 'w') as file:
                subprocess.run(command1, shell=True, stdout=file, check=True)
            with open(output_path2, 'w') as file:
                subprocess.run(command2, shell=True, stdout=file, check=True)
            with open(output_path3, 'w') as file:
                subprocess.run(command3, shell=True, stdout=file, check=True)

            diff_files = {
                'line_diff': url_for('serve_diffs', filename='line.html', session_id=session['session_id'],origin='main'),
                'no_line_diff': url_for('serve_diffs', filename='no_line.html', session_id=session['session_id'],origin='main'),
                'side_by_side_diff': url_for('serve_diffs', filename='side_by_side.html', session_id=session['session_id'],origin='main')
            }


    

    return render_template("main.html", 
                           error_message=error_message,
                           code1=code1,
                           code2=code2,
                           newInput1=newInput1,
                           newInput2=newInput2,
                           uname1=uname1,
                           uname2=uname2,
                           show_checkbox_page=show_checkbox_page,
                           diff_files=diff_files)


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
        'folder_diff': url_for('serve_diffs', filename='folder_diff.html', session_id=session['session_id'],origin='repo'),
        'folder_diff_mod': url_for('serve_diffs', filename='folder_diff_modifications_only.html', session_id=session['session_id'],origin='repo'),
        'line_diff': url_for('serve_diffs', filename='line.html', session_id=session['session_id'],origin='repo'),
        'no_line_diff': url_for('serve_diffs', filename='no_line.html', session_id=session['session_id'],origin='repo'),
        'side_by_side_diff': url_for('serve_diffs', filename='side_by_side.html', session_id=session['session_id'],origin='repo')
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




@app.route("/diffs/<session_id>/<origin>/<path:filename>")
def serve_diffs(session_id, origin, filename):
    if origin == 'main':
        diff_dir = os.path.join(st.repo_store, session_id, "main_diff_path")
    elif origin == 'repo':
        diff_dir = os.path.join(st.repo_store, session_id, 'diff')
    else:
        return "Invalid origin", 400

    file_path = os.path.join(diff_dir, filename)
    if os.path.exists(file_path):
        return send_from_directory(diff_dir, filename)
    else:
        return "File not found", 404




if __name__ == "__main__":
    app.run(debug=True)




