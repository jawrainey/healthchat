from flask import render_template
from flask.ext.socketio import emit
from messenger import Messenger
from app import app, socketio


@app.route('/')
def index():
    # TODO: use bootstrap, and remove js/css to separate files.
    return render_template('index.html')


@socketio.on('user', namespace='/chat')
def user_received_message(user_message):
    # TODO: currently, empty messages can be sent.
    # TODO: save message to database for improvements later...
    add_new_lines_user_message = user_message['data'].replace('\n', '</br>')
    emit('response', {'type': 'received', 'data': add_new_lines_user_message})
    open_ended_question = Messenger().open_ended_question(user_message['data'])
    emit('response', {'type': 'service', 'data': open_ended_question})


@socketio.on('connect', namespace='/chat')
def on_connection():
    # Once a connection is established, we want to send the initial message.
    emit('response', {'type': 'service', 'data': Messenger().initial_message()})
