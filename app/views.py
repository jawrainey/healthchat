from flask import render_template
from flask.ext.socketio import emit
from messenger import Messenger
from app import app, db, models, socketio


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


@socketio.on('vote', namespace='/chat')
def on_vote(data):
    # TODO: what about initial OEQ and clarification question?
    __cast_vote(data['question'], data['rating'])
    # Only 'update' current question if user is dissatisfied.
    if 'down' in data['rating']:
        emit('vote response',
             {'data': Messenger().open_ended_question(data['prev_user_msg'])})


def __cast_vote(_question, _rating):
    '''
    Updates the rating of a question voted for by a user.

    Args:
        question (str): The question to vote against.
        rating (str): can either be 'up' or 'down'.
    '''
    row = models.Question.query.filter_by(question=_question).first()
    # The limits exist to not exceed threshold (0, 1)
    if row:
        if 'up' in _rating and row.rating <= .9:
            row.rating += .1
        if 'down' in _rating and row.rating >= .1:
            row.rating -= .1
        db.session.commit()
