from flask import Flask
from flask.ext.socketio import SocketIO

app = Flask(__name__)
app.debug = True

socketio = SocketIO(app)

from app import views
