from flask import Blueprint, send_from_directory

import os
import settings

st = settings.PrepareSettings()

serve_blueprint = Blueprint('diff', __name__)

@serve_blueprint.route("/diffs/<session_id>/<origin>/<path:filename>")
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
