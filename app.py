import os
from flask import Flask,abort,render_template,request,redirect,url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './upload'
ALLOWED_EXTENSIONS = set(['txt','jpg','png','jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join("upload", file.filename))
        return render_template('check.html')
    return render_template('check.html')


if __name__ == "__main__":
    app.run(debug=True)
