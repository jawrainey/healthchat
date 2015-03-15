from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.socketio import SocketIO
import os

# The main application folder
_basedir = os.path.abspath(os.path.dirname('..'))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'test.db')

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'supersectetsessionrequiredkeyforsecurityreasons'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

socketio = SocketIO(app)
db = SQLAlchemy(app)

from app import views, models
