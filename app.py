from flask import Flask,abort,render_template,request,redirect,url_for,flash
import os
import urllib.request
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'upload/'

app.secret_key = "Human pose estimation"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['jpg','png','jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Image successfully uploaded and displayed below')
        return render_template('check.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg')
        return redirect('/')

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('templates/check', filename='upload/' + filename))


if __name__ == "__main__":
    app.run(debug=True)
