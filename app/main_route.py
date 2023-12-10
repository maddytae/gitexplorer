from flask import Blueprint, render_template, request, session, url_for, redirect
import os
import subprocess
import uuid

import logging
logging.basicConfig(level=logging.DEBUG)

import utilities as ut
import settings
st = settings.PrepareSettings()



main_blueprint = Blueprint('main', __name__)

@main_blueprint.route("/", methods=["GET", "POST"])
def main():
    error_message = None
    show_checkbox_page = True 
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
        ut.recreate_directory(main_diff_dir)


        if 'sshAddress' in request.form:
            sshAddress = request.form.get("sshAddress")
            session["sshAddress"] = sshAddress
            if sshAddress:
                repo_name = sshAddress.split('/')[-1].replace('.git', '')
                # Set paths for repo and diff
                repo_path = os.path.join(session_dir, repo_name)
                diff_path = os.path.join(session_dir, 'diff')

                # ut.clear_directory(diff_path) #clears the diff_path

                # Store paths in session
                session['repo_path'] = repo_path
                session['diff_path'] = diff_path

                try:
                    ut.repo_cloning(sshAddress, repo_path, st.repo_size_limit)
                    return redirect(url_for("repo.repo", repo_name=repo_name))
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
                    ut.process_link(newInput1,file_path1,st.link_size_limit) # this should save file1.txt in the destination folder
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
                    ut.process_link(newInput2,file_path2,st.link_size_limit)
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
                'line_diff': url_for('diff.serve_diffs', filename='line.html', session_id=session['session_id'],origin='main'),
                'no_line_diff': url_for('diff.serve_diffs', filename='no_line.html', session_id=session['session_id'],origin='main'),
                'side_by_side_diff': url_for('diff.serve_diffs', filename='side_by_side.html', session_id=session['session_id'],origin='main')
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

