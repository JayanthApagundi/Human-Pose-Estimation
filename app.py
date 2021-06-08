from flask import Flask,abort,render_template,request,redirect,url_for,flash
import os
import urllib.request
from werkzeug.utils import secure_filename
import cv2
import mediapipe as mp

app = Flask(__name__)

UPLOAD_FOLDER = 'static/upload/'
DOWNLOAD_FOLDER = 'static/download/'

app.secret_key = "Human pose estimation"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['jpg','png','jpeg'])

mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if 'file' not in request.files:
        # flash('No file part')
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        # flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # flash('Image successfully uploaded and displayed below')
        process_file(os.path.join(UPLOAD_FOLDER, filename), filename)
        data = {
            "processed_img": 'static/download/' + filename,
            "uploaded_img": 'static/upload/' + filename
        }
        return render_template('check.html', data=data)
    else:
        # flash('Allowed image types are - png, jpg, jpeg')
        return redirect('/')

def process_file(path, filename):
    display_image(path, filename)

@app.route('/display/<filename>')
def display_image(path, filename):
    with mpPose.Pose(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=0.5) as pose:
        # while True:
        image = cv2.imread(path)
        # image_height, image_width, _ = image.shape
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        # print(results.pose_landmarks)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(image, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = image.shape
                # print(id, lm)
                cx, cy = int(lm.x * w), int(lm.y * h)  # to get pixel value of x,y landmarks
                cv2.circle(image, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        # img = cv2.resize(image, (1060, 980))  # Resize image
        cv2.imwrite(f"{DOWNLOAD_FOLDER}{filename}", image)
        # cv2.imshow("Image", image)
        # cv2.waitKey(0)

    # return redirect(url_for('static', filename='upload/' + filename), code=301)


if __name__ == "__main__":
    app.run(debug=True)
