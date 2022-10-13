from flask import Flask, render_template, flash, redirect, url_for, request, send_from_directory
from forms import FastaForm, parameters
import os
import uuid
from werkzeug.exceptions import HTTPException
from celery import Celery
from dashApp import create_dash_app
from dotenv import load_dotenv
from tasks import scan
from celery.result import AsyncResult

app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY' ] = os.getenv("SECRET_KEY")
app.config['UPLOAD_EXTENSIONS'] = os.getenv("UPLOAD_EXTENSIONS")
app.config['UPLOAD_PATH'] = os.getenv("UPLOAD_PATH")
app.config['CELERY_BROKER_URL'] = os.getenv("CELERY_BROKER_URL")
app.config['CELERY_RESULT_BACKEND'] = os.getenv("CELERY_RESULT_BACKEND")

celery= Celery('tasks',  
                broker=app.config['CELERY_BROKER_URL'],
                backend=app.config['CELERY_RESULT_BACKEND'])

create_dash_app(app)

@app.route("/")
def uploader():
    form = FastaForm()
    return render_template('uploader.html', form = form, parameters=parameters, title="Home")


@app.route('/upload', methods = ['GET','POST'])
def upload():
    if request.method == "POST":
        uploaded_file = request.files['fasta_file']
        file_name = uploaded_file.filename
        param_selections = []
        params = []
        params_arg = ""


        for x in parameters['Dinucleotide']:
                param_selections.append([x,request.form.getlist(x)])
        for y in parameters['Trinucleotide']:
                param_selections.append([y,request.form.getlist(y)])
        for param in param_selections:
            if param[1] == ['on']:
                params.append(param[0])
        for para in params:
            params_arg += para + ","
        data = {
            'windowWidth':  request.form['windowWidth'],
            'params_arg' : params_arg,
            'seq_no' : "-",
        }
        
        if 'inc-conc' not in request.form:
            data['inc-conc'] = "off"
        else:
            data['inc-conc'] = "on"

        if len(params) == 0:
            flash("Please select some parameters", "danger")

        if file_name != '':
            file_ext = os.path.splitext(file_name)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                flash("Please provide FASTA file", "danger")
            else:
                upload_path = os.path.join(app.config['UPLOAD_PATH'])
                file_name = upload_path + str(uuid.uuid4()) + ".fasta"
                uploaded_file.save(file_name)
                data['file_name'] = file_name
        else:
            if request.form['fasta_text'] != '':
                upload_path = os.path.join(app.config['UPLOAD_PATH'])
                file_name= upload_path + "/" + str(uuid.uuid4()) + ".fasta"
                with open(file_name,'w') as f:
                    f.write(request.form['fasta_text'])
                data['file_name'] = file_name
                data['seq_no'] = request.form['seq_no']
            else:
                flash("No file selected", "danger") 
        upload_task = scan.apply_async(args=[data])
        return redirect(url_for("job", task = upload_task,parameters_selected=params_arg[:-1],seq_no = data['seq_no'],inc_conc = data['inc-conc']))

    return redirect(url_for('uploader'))


@app.route('/<task>/<parameters_selected>/<seq_no>/<inc_conc>')
def job(task, parameters_selected,seq_no,inc_conc):
    parameters_selected = parameters_selected.replace(","," , ")
    if AsyncResult(task).ready() == False:
        status = "Pending"
    else:
        status = "Successful"
        return redirect(url_for("results",job_id = task,parameters_selected=parameters_selected, seq_no = seq_no,inc_conc=inc_conc))
    return render_template('job.html', job_id = task, status = status, parameters = parameters_selected, title = "Pending")

@app.route('/results/<job_id>/<parameters_selected>/<seq_no>/<inc_conc>')
def results(job_id, parameters_selected,seq_no,inc_conc):
    new_folder = AsyncResult(job_id).get()
    return render_template('results.html',job_id = job_id, new_folder = new_folder, parameters_selected = parameters_selected, seq_no = seq_no, title = "Results",inc_conc=inc_conc)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

@app.route('/parameters_page')
def parameters_page():
    return render_template('parameters_page.html')
    
@app.route('/result_interpretation')
def result_interpretation():
    return render_template('result_interpretation.html')


@app.route('/static/<path:filename>', methods = ['GET','POST'])
def download(filename):
    download_folder = "static/"
    return send_from_directory(directory = download_folder, path = filename, as_attachment=True)


@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return render_template("error.html", code = code)


if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
