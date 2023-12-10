import os
from flask import Flask
from app.repo_route import repo_blueprint
from app.main_route import main_blueprint
from app.serve_route import serve_blueprint
import settings
import shutil
import time
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

import logging

logging.basicConfig(level=logging.DEBUG)

st = settings.PrepareSettings()

flask_app = Flask(__name__)
flask_app.secret_key = "khiadh2727sdhks888s"
# Register the blueprint
flask_app.register_blueprint(repo_blueprint)
flask_app.register_blueprint(main_blueprint)
flask_app.register_blueprint(serve_blueprint, url_prefix='/')

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

if __name__ == "__main__":
    flask_app.run(debug=True)




