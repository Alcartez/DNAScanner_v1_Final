import os
import shutil
from celery import Celery
from dotenv import load_dotenv
import uuid

load_dotenv()

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")


celery= Celery('tasks',  
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)

@celery.task(name="app.scan", bind = True)
def scan(self,data):
    output_folder = str(uuid.uuid4())
    run_script = os.system(f"python3 DNAScanner.py {data['file_name']}%%{data['windowWidth']}%%{data['params_arg']}%%{output_folder}")
    if (run_script == 0):
        print("Making ZIP FILE")
        shutil.make_archive(f"static/Output/{output_folder}", 'zip', f"static/output/{output_folder}")
        print("Done")    
    else:
        os.remove(data['file_name'])
        shutil.rmtree(f"static/Output/{output_folder}")
    return output_folder
