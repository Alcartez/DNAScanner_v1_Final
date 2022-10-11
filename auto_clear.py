import os
import shutil
from celery import Celery
import time


CELERY_BROKER_URL = 'redis://default:redispw@localhost:55000'
CELERY_RESULT_BACKEND = 'redis://default:redispw@localhost:55000'


celery= Celery('auto_clear',  
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)
                
@celery.task(name="auto_clear")
def auto_clear():
    upload_path = 'instance/uploads/'
    output_folder = os.path.join("static/Output/")
    list_dir = [x[0] for x in os.walk(output_folder)]
    for x in list_dir[1:]:
        elapsed = (time.time() - os.stat(x).st_mtime) / 86400
        if elapsed >= 0.007:
            print("Deleting " + x)
            shutil.rmtree(x)

    list_files = [x[0] for x in os.walk(upload_path)]
    for x in list_files[1:]:
        elapsed = (time.time() - os.stat(x).st_mtime) / 86400
        if elapsed >= 0.007:
            print("Deleting " + x)
            shutil.rmtree(x)

celery.conf.beat_schedule = {
    "run-me-every-day": {
    "task": "auto_clear",
    "schedule": 86400.0
    }
}