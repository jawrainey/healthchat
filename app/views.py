from flask import render_template
from flask.ext.socketio import emit
from app import app, socketio


@app.route('/')
def index():
    # TODO: use bootstrap, and remove js/css to separate files.
    return render_template('index.html')


@socketio.on('user', namespace='/chat')
def user_received_message(user_message):
    # TODO: currently, empty messages can be sent.
    # TODO: save message, parse it, generate response, send theirs, then ours.
    emit('response', {'data': 'User: ' + user_message['data']})
    emit('response', {'data': 'Client: appropriate OEQ response!!'})


@socketio.on('connect', namespace='/chat')
def on_connection():
    # Once a connection is established, we want to send the initial message.
    emit('response', {'data': 'Client: Initial opening question'})
