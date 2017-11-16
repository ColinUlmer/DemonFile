import hashlib
import random
import os
import pyrax

from flask import Flask, render_template, request, jsonify
from twilio.rest import Client

from models import db, File, User
from config import app

pyrax.set_setting("identity_type", "rackspace")
pyrax.set_default_region(app.config['RACKSPACE_REGION'])
pyrax.set_credentials(app.config['RACKSPACE_USERNAME'], app.config['RACKSPACE_SECRET'])

def getUserFiles(phone_number):
    hashed_phone = hashlib.sha224(phone_number).hexdigest()
    user_obj = User.query.filter_by(phone=hashed_phone).first()
    files = []
    files_obj = File.query.filter_by(userID=user_obj.id)
    for f in files_obj:
        tmp = {}
        tmp['filename'] = f.file_name
        tmp['type'] = f.file_type
        tmp['size'] = f.size
        files.append(tmp)
    return files

def isPhone(phone_input):
    if len(phone_input) != 10 or not phone_input.isdigit():
        return False
    return True

def isCode(code_input):
    if len(code_input) != 5 or not code_input.isdigit():
        return False
    return True

def generateVerificationCode():
    return str(random.randrange(10000, 99999))

def send_sms(to_number, body):
    account_sid = app.config['TWILIO_SID']
    auth_token = app.config['TWILIO_SECRET']
    twilio_number = app.config['TWILIO_NUMBER']
    client = Client(account_sid, auth_token)
    client.api.messages.create(to_number,
                           from_=twilio_number,
                           body=body)

def verifyCredentials(phone, code):
    hashed_phone = hashlib.sha224(phone).hexdigest()
    hashed_code = hashlib.sha224(code).hexdigest()
    user_credentials = User.query.filter_by(phone=hashed_phone).first()
    if user_credentials and user_credentials.code == hashed_code:
        return True
    return False

@app.route("/verify", methods=['POST'])
def verifyPhone():
    """
    Check if User number already exists, if not create an account and send verification code
    """
    if not request.values['phone'] or request.values['phone'] == "" or not isPhone(request.values['phone']):
        return jsonify({'status':301, 'response':'Invalid phone number entered'})
    to_number = request.values['phone']
    hashed_phone = hashlib.sha224(to_number).hexdigest()
    if User.query.filter_by(phone=hashed_phone).first():
        return jsonify({'status':300, 'response':'User already exists'})
    verification_code = generateVerificationCode()

    print "Code: %s\n\n" % verification_code
#    send_sms(to_number, verification_code)

    hashed_code = hashlib.sha224(verification_code).hexdigest()
    new_user = User(phone=hashed_phone, code=hashed_code)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'status': 200})

@app.route("/login", methods=['POST'])
def login():
    phone_number = request.values['phone']
    code = request.values['code']
    if not code or code == "" or not isCode(code):
        return jsonify({'status': 303, 'data': "No code provided"})
    if verifyCredentials(phone_number, code):
        files = getUserFiles(phone_number)
        return jsonify({'status': 200, 'data': files})
    else:
        return jsonify({'status': 304, 'data': "Invalid Credentials"})

@app.route("/upload", methods=['POST'])
def fileUpload():
    """
    Uploads user file to Rackspace and adds the location and
    user reference to the database
    """
    if request.method != "POST": #or 'user-file' not in request.files.keys(): #or 'phone' not in request.headers.keys():
        return jsonify({'status': 305, 'data': 'Bad Upload'})

    if len(request.files.values()) <= 0:
        return jsonify({'status': 306, 'data': 'No file received for upload'})

    if not request.headers['phone']:
        return jsonify({'status': 307, 'data':'Incorrect headers'})

    hashed_phone = hashlib.sha224(request.headers['phone']).hexdigest()
    user_obj = User.query.filter_by(phone=hashed_phone).first()
    if not user_obj:
        return jsonify({'status': 308, 'data':'Unable to find User'})

    cf = pyrax.cloudfiles.get_container(app.config['RACKSPACE_CONTAINER_NAME'])

    for f in request.files.values():
        tmp_file_path = os.path.join(app.config['UPLOAD_DIR'], f.filename)
        f.save(tmp_file_path)
        cf.upload_file(tmp_file_path)
        file_obj = File(userID=user_obj.id, file_name=f.filename, file_type=f.content_type, size=os.path.getsize(tmp_file_path))
        os.remove(tmp_file_path)
        db.session.add(file_obj)
    db.session.commit()


@app.route("/data/update-files", methods=['POST'])
def updateFiles():
    """
    Accepts User phone and code then returns JSON file table
    """
    if request.method != "POST":
        return jsonify({'status':309, 'data':'Bad File Request'})
    if not request.values['phone'] or not request.values['code']:
        return jsonify({'status':309, 'data':'Bad File Request'})
    if verifyCredentials(request.values['phone'], request.values['code']):
        return jsonify({'status':200, 'data': getUserFiles(request.values['phone'])})
    else:
        return jsonify({'status': 304, 'data': "Invalid Credentials"})


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
