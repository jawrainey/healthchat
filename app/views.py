from flask import render_template
from flask.ext.socketio import emit
from messenger import Messenger
from app import app, db, models, socketio


@app.route('/')
def index():
    '''
    Homepage of website that contains the chat application.
    '''
    return render_template('index.html')


@socketio.on('user', namespace='/chat')
def user_received_message(user_message):
    '''
    Receives a clients message and sends an appropriate contextual response.

    Args:
        user_message (dict): Contains the user message (data).
        TODO: simplify argument by sending only a string.
    '''
    # TODO: currently, empty messages can be sent.

    add_new_lines_user_message = user_message['data'].replace('\n', '</br>')
    emit('response', {'type': 'received', 'data': add_new_lines_user_message})

    open_ended_question = Messenger().open_ended_question(user_message['data'])
    emit('response', {'type': 'service', 'data': open_ended_question})


@socketio.on('connect', namespace='/chat')
def on_connection():
    '''
    Send initial opening message and instructions on connection.
    '''
    emit('response', {'type': 'service', 'data': Messenger().initial_message()})


@socketio.on('vote', namespace='/chat')
def on_vote(data):
    '''
    Improve rating of OEQ when the up/down buttons clicked.
    Note: a response is only sent IFF the user is dissatisfied (downvotes).

    Args:
        data (dict): contains users previous message and feedback (rating).
    '''
    # TODO: what about initial OEQ and clarification question?
    __cast_vote(data['question'], data['rating'])
    if 'down' in data['rating']:
        emit('vote response',
             {'data': Messenger().open_ended_question(data['prev_user_msg'])})


def __cast_vote(_question, _rating):
    '''
    Updates the rating of a question voted for by a user.

    Args:
        _question (str): The question to vote against.
        _rating (str): can either be 'up' or 'down'.
    '''
    row = models.Question.query.filter_by(question=_question).first()
    # The limits exist to not exceed threshold (0, 1)
    if row:
        if 'up' in _rating and row.rating <= .9:
            row.rating += .1
        if 'down' in _rating and row.rating >= .1:
            row.rating -= .1
        db.session.commit()
