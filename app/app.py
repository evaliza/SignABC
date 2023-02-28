import requests
import os
from werkzeug.utils import secure_filename
import random
from camera import VideoCamera
from camera1 import Analyse
from model.admin import Admin
from model.user import User
from model.letter import Letter
from model.predict import Predict
from mail import Email
import hashlib  # MD5
from flask import Flask, render_template, redirect, request, session, Response, url_for
from flask_session import Session
import flask_monitoringdashboard as dashboard
import traceback
from datetime import datetime



import os


app = Flask(__name__)

# monotoring
dashboard.config.init_from(file='config.cfg')  # In order to configure the Dashboard with a configuration-file,
dashboard.bind(app) # add monotoring

from logging.handlers import SMTPHandler
from logging import FileHandler, WARNING, ERROR, CRITICAL,  INFO, Formatter

file_handler = FileHandler('logs/errorlog.txt')
file_handler.setLevel(ERROR)
app.logger.addHandler(file_handler)


mail_handler = SMTPHandler(
    mailhost='127.0.0.0',
    fromaddr='server-error@domain.com',
    toaddrs=['ilizaeve@gmail.com'],
    subject='Application Error'
)
mail_handler.setLevel(ERROR)
mail_handler.setFormatter(Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
app.logger.addHandler(mail_handler)

#session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
s = requests.Session()

#uploads files
UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




def gen(camera):
    while True:
        frame = camera.get_frame_hand()
        yield (b'--frame\r\n'
            b'Content - Type: image/jpeg\r\n\r\n' + frame
            + b'\r\n\r\n')

def random_letter():
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    index = random.randint(0, 25)
    return alphabet[index]

# The route
@app.route('/cam/', methods=['GET', 'POST'])
def cam():
    try:
        #raise ValueError('A very specific bad thing happened.')
        return render_template('cam.html')

    except Exception as err:
        template = "{0}: An exception of type {1} occurred. Arguments:{2!r}"
        message = template.format(str(datetime.now()), type(err).__name__, err.args)
        app.logger.error(message)
        template = "{0}: An exception has been occurred:\n{1}"
        message = template.format(str(datetime.now()), traceback.format_exc())
        Email.sendMail("SignABC error", message)
        return render_template('404.html')



@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/deconnection')
def deconnection():
    session.clear()
    return render_template('deconnection.html')

@app.route('/lessons')
def lessons():
    l = Letter()
    return render_template('lessons.html', letters=l.readAll())


@app.route('/start', methods=['GET', 'POST'])
def upload_file():
    try:
        newLetter = random_letter()
        if request.method == 'POST':
            file = request.files['file']
            if file.filename == '':
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                analyse = Analyse(filename, session['name'], app.config['UPLOAD_FOLDER'])
                analyse.get_frame()
                percent = analyse.get_percent()
                print(("percent ********* : ", percent))
                imageUpload = analyse.get_imageUpload()
                landmarks = analyse.get_landmarks()
                fingerspell = analyse.get_letterPredict()
                l = request.form['letter']
                print(("letter searched ********* : ", l))
                print("letter : ", l)
                if l != "":
                    predict = Predict()
                    predict.create(l,percent, session['email'], imageUpload, landmarks)

            return render_template('start.html', imageUpload=imageUpload
                                   , percent=percent, 
                                   newLetter=newLetter,
                                   landmarks=landmarks, 
                                   fingerspell=fingerspell, 
                                   lettersearched = l)
    except Exception as err:
        template = "An exception has been occurred:\n{0}"
        message = template.format(traceback.format_exc())
        Email.sendMail("SignABC error", message)

    return render_template('start.html', newLetter=newLetter)


@app.route('/results/', methods=['GET', 'POST'])
def results():
    try:
        predict = Predict()
        return render_template('results.html', predicts=predict.selectByUser(session['name']))
    
    except Exception as err:
        template = "An exception has been occurred:\n{0}"
        message = template.format(traceback.format_exc())
        Email.sendMail("SignABC error", message)
    

@app.route('/login/', methods=['GET', 'POST'])
def login():
    try:
        # raise ValueError('A very specific bad thing happened.') # lever une exception pour test(mail)
        if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
            email = request.form['email'].strip()
            pwd = request.form['password'].strip()
            pwd = hashlib.md5(pwd.encode()).hexdigest()
            
            admin = Admin()
            res = admin.identification(email, pwd)
            for raw in res:
                print (raw[0], raw[1])
                session['name'] = raw[0]
                session['email'] = raw[1]
                session['role'] = raw[2]
                return redirect(url_for('cam', code=302))

    except Exception as err:
        template = "An exception has been occurred:\n{0}"
        message = template.format(traceback.format_exc())
        Email.sendMail("SignABC error", message)

    return render_template('login.html')


@app.route('/create_user/', methods=['GET', 'POST'])
def create_user():    
    try:
        admin = Admin()
        req = admin.getRole()
        if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
            name = request.form['name']
            lastname = request.form['lastname']
            email = request.form['email']
            pwd = request.form['password']
            role = request.form['role']
            if "doneUser" in request.form:
                # form completed by user
                u = User()
                r = u.createUser(name, lastname, email, pwd, role)

                if r is None:
                #une erreur s est produite
                    return render_template('create_user.html', roles=req,  err=1)

                session['name'] = name
                session['email'] = email
                session['role'] = role
                return redirect(url_for('cam', code=302))
            else:
                r = admin.createUser(name, lastname, email, pwd, role)
                print("create user :", r)
                if r == False:
                    #une erreur s est produite
                    return render_template('create_user.html', roles=req, err=1)

                return redirect(url_for('list_user', code=302))
    

        return render_template('create_user.html', roles=req)

    except Exception as err:
        template = "An exception has been occurred:\n{0}"
        message = template.format(traceback.format_exc())
        Email.sendMail("SignABC error", message)

    

@app.route('/list_user/', methods=['GET', 'POST'])
def list_user():
    try:
        admin = Admin()
        return render_template('list_user.html', users=admin.selectUser())
    except Exception as err:
        template = "An exception has been occurred:\n{0}"
        message = template.format(traceback.format_exc())
        Email.sendMail("SignABC error", message)


@app.route('/monotoring/', methods=['GET', 'POST'])
def monotoring():
    try:
        return render_template('monotoring.html')
    except Exception as err:
        template = "An exception has been occurred:\n{0}"
        message = template.format(traceback.format_exc())
        Email.sendMail("SignABC error", message)

@app.route('/', methods=['POST', 'GET'])
def index():
    try:
        if request.method == 'POST':
            return render_template("index.html")

        return render_template('index.html')
    except Exception as exc:
        app.logger.error("message berreur")
        #sendMail("test", "detailString")


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
