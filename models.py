import datetime
from flask_sqlalchemy import SQLAlchemy

from config import app

db = SQLAlchemy(app)

class User(db.Model):
    id =                   db.Column(db.Integer, primary_key=True)
    phone =                db.Column(db.String(128), unique=True, nullable=False)
    code =                 db.Column(db.String(128), nullable=False)
    expiration_time =      db.Column(db.DateTime, nullable=False, default=datetime.datetime.now() + datetime.timedelta(hours=3))
    current_usage =        db.Column(db.Float, nullable=False, default=0.0) #size in megabytes

class File(db.Model):
    id =                db.Column(db.Integer, primary_key=True)
    userID =            db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_name =         db.Column(db.String(240), nullable=False)
    file_type =         db.Column(db.String(80), nullable=False)
    url =               db.Column(db.String(256), nullable=True)
    size =              db.Column(db.Float, nullable=False, default=0.0) #size in megabytes
