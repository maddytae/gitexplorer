from flask import Blueprint, render_template, request, session, url_for
import os
import subprocess
import utilities as ut
import settings
st = settings.PrepareSettings()
repo_blueprint = Blueprint('repo', __name__)

@repo_blueprint.route("/repo/<repo_name>", methods=["GET", "POST"])
def repo(repo_name):

    repo_path=session.get('repo_path', '')
    diff_path=session.get('diff_path','')
    ut.recreate_directory(diff_path)



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
            
            command3 = f"git -C {repo_path} diff  -U10000 {selected_commit1} {selected_commit2} {selected_filePath} |delta --line-numbers | ansifilter --encoding=UTF-8 --html"
            command4 = f"git -C {repo_path} diff  -U10000 {selected_commit1} {selected_commit2} {selected_filePath}|delta  | ansifilter --encoding=UTF-8 --html"
            command5 = f"git -C {repo_path} diff -U10000 {selected_commit1} {selected_commit2} {selected_filePath}|delta --width=150 --side-by-side | ansifilter --encoding=UTF-8 --html"
  
            with open(output_path3, 'w') as file:
                subprocess.run(command3, shell=True, stdout=file, check=True)
            with open(output_path4, 'w') as file:
                subprocess.run(command4, shell=True, stdout=file, check=True)
            with open(output_path5, 'w') as file:
                subprocess.run(command5, shell=True, stdout=file, check=True)


    diff_files = {
        'folder_diff': url_for('diff.serve_diffs', filename='folder_diff.html', session_id=session['session_id'],origin='repo'),
        'folder_diff_mod': url_for('diff.serve_diffs', filename='folder_diff_modifications_only.html', session_id=session['session_id'],origin='repo'),
        'line_diff': url_for('diff.serve_diffs', filename='line.html', session_id=session['session_id'],origin='repo'),
        'no_line_diff': url_for('diff.serve_diffs', filename='no_line.html', session_id=session['session_id'],origin='repo'),
        'side_by_side_diff': url_for('diff.serve_diffs', filename='side_by_side.html', session_id=session['session_id'],origin='repo')
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
                           diff_files=diff_files,
                           url_for_repo=url_for('repo.repo', repo_name=repo_name))
