import os
import pyrax

from flask import Flask

app = Flask(__name__)
app.config['DEBUG'] = False
app.config['UPLOAD_DIR'] = os.getcwd() + '/store'

#Heroku
app.config['SQLALCHEMY_DATABASE_URI'] = ''

#Twilio
app.config['TWILIO_SID'] = ''
app.config['TWILIO_SECRET'] = ''
app.config['TWILIO_NUMBER'] = ''

#Rackspace, cause fuck S3 for deleting my account
app.config['RACKSPACE_USERNAME'] = ''
app.config['RACKSPACE_SECRET'] = ''
app.config['RACKSPACE_REGION'] = ''
app.config['RACKSPACE_CONTAINER_NAME'] = ''
