from flask import render_template, request, Blueprint
from flask.ext.socketio import emit
from messenger import Messenger
from app import db, models, socketio

# Abstraction required to create an application factory.
main = Blueprint('main', __name__)


@main.route('/')
def index():
    '''
    Homepage of website that contains the chat application.
    '''
    return render_template('index.html')


@main.route('/about')
def about():
    '''
    Contains detailed information on the project, including:
        application purpose, user participation, instructions, & privacy policy.
    '''
    return render_template('about.html')


@main.app_errorhandler(404)
def page_not_found(e):
    '''
    If a 404 occurs: inform the user and redirect them to /about/ in a fun way.
    '''
    return render_template('404.html'), 404


@socketio.on('user', namespace='/chat')
def user_received_message(user_message):
    '''
    Receives a clients message and sends an appropriate contextual response.

    Args:
        user_message (string): Contains the user message.
    '''
    add_new_lines_user_message = user_message.replace('\n', '</br>')
    emit('response', {'type': 'received', 'data': add_new_lines_user_message})

    open_ended_question = Messenger().open_ended_question(user_message)
    emit('response', {'type': 'service', 'data': open_ended_question})

    cid = request.namespace.socket.sessid  # current conversation id
    db.session.add(models.Message(
        status='received', content=user_message, conversation_id=cid))
    db.session.add(models.Message(
        status='service', content=open_ended_question, conversation_id=cid))
    db.session.commit()


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


@socketio.on('feedback', namespace='/chat')
def on_feedback(data):
    '''
    Saves user feedback form data to the database for later review.

    Args:
        data (dict): stores the System Usability Scale (SUS) results, and the
        results for a free-form general feedback.
    '''
    db.session.add(models.Feedback(sus=data['sus'], general=data['general']))
    db.session.commit()
    # TODO: respond with a 'thanks for submitting feedback...'


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
