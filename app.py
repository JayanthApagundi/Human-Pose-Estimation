from flask import Flask, render_template, request, redirect, url_for, Response, flash
import os
from werkzeug.utils import secure_filename
import cv2
import mediapipe as mp

app = Flask(__name__)

UPLOAD_FOLDER = 'static/upload/'
DOWNLOAD_FOLDER = 'static/download/'

app.secret_key = "Human pose estimation"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['jpg','png','jpeg','mp4','avi'])

mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading', 'danger')
        return redirect('/')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        process_file(os.path.join(UPLOAD_FOLDER, filename), filename)
        data = {
            "processed_img": 'static/download/' + filename,
            "uploaded_img": 'static/upload/' + filename
        }
        return render_template('image.html', data=data)
    else:
        flash('Allowed image types are - png, jpg, jpeg', 'danger')
        return redirect('/')

def process_file(path, filename):
    display_image(path, filename)

@app.route('/display/<filename>')
def display_image(path, filename):
    with mpPose.Pose(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=0.5) as pose:
        image = cv2.imread(path)
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        # print(results.pose_landmarks)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(image, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = image.shape
                # print(id, lm)
                cx, cy = int(lm.x * w), int(lm.y * h)  # to get pixel value of x,y landmarks
                cv2.circle(image, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        cv2.imwrite(f"{DOWNLOAD_FOLDER}{filename}", image)

@app.route('/vidupload', methods=['GET', 'POST'])
def vidupload():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        flash('No video selected for uploading', 'danger')
        return redirect('/')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return Response(displayvid(os.path.join(UPLOAD_FOLDER, filename)), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        flash('Allowed video type - mp4', 'danger')
        return redirect('/')

@app.route('/displayvid/<filename>', methods=['GET', 'POST'])
def displayvid(path):
    cap = cv2.VideoCapture(path)
    while True:
        success, img = cap.read()
        if success == False:
            break
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)

        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks,mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                # print(id, lm)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def live():
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        if success == False:
            break
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)

        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks,mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                # print(id, lm)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed', methods=['GET', 'POST'])
def video_feed():
    return Response(live(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
