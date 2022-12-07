
import os
import subprocess

from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from doc_merger import get_all_word_files, merge
from pdf_merger import get_all_pdf_files
from pdf_merger import merge as merge_pdf

BASE_DIR = os.getcwd()

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'

def doc2pdf_linux(doc):
    """
    convert a doc/docx document to pdf format (linux only, requires libreoffice)
    :param doc: path to document
    """
    cmd = 'libreoffice --convert-to pdf'.split() + [doc]
    cmd += ['--outdir', 'output']
    print(cmd)
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    p.wait(timeout=100)
    stdout, stderr = p.communicate()
    print(stderr)
    if stderr:
        raise subprocess.SubprocessError(stderr)


@app.route('/', methods=['GET'])
def home():
    os.system('rm -r uploads')
    try:
        os.mkdir('uploads')
        os.chdir('uploads')
        os.mkdir('output')
        os.chdir('..')
    except Exception as e:
        print(e)
    return render_template('index.html')


@app.route('/doc2pdf', methods=['POST'])
def doc2pdf():
    print(request.files)
    for file in request.files.getlist('files'):
        filename = file.filename
        file.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                secure_filename(filename)
            )
        )
    os.chdir('uploads')
    for file in os.listdir():
        if not file.endswith('.docx'):
            continue
        doc2pdf_linux(file)
    os.system('zip output.zip output/*')
    os.chdir(BASE_DIR)
    return render_template('download.html', operation='doc2pdf')


@app.route('/doc_merge', methods=['POST'])
def doc_merge():
    for file in request.files.getlist('files'):
        filename = file.filename
        file.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                secure_filename(filename)
            )
        )
    os.chdir('uploads')
    merge(get_all_word_files())
    os.chdir(BASE_DIR)
    return render_template('download.html', operation='doc_merge')


@app.route('/pdf_merge', methods=['POST'])
def pdf_merge():
    for file in request.files.getlist('files'):
        filename = file.filename
        file.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                secure_filename(filename)
            )
        )
    os.chdir('uploads')
    merge_pdf(get_all_pdf_files())
    os.chdir(BASE_DIR)
    return render_template('download.html', operation='pdf_merge')


@app.route('/download', methods=['GET'])
def download():
    operation = request.args.get(
        'operation',
        default='doc2pdf',
        type=str
    )
    if operation == 'doc2pdf':
        return send_from_directory(
            app.config["UPLOAD_FOLDER"],
            'output.zip'
        )
    elif operation == 'doc_merge':
        return send_from_directory(
            app.config["UPLOAD_FOLDER"],
            'output.docx'
        )
    elif operation == 'pdf_merge':
        return send_from_directory(
            app.config["UPLOAD_FOLDER"],
            'output.pdf'
        )
