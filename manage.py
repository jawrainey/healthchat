from flask.ext.script import Manager
from app import create_app, socketio, messenger, db, models
from settings import DevConfig, ProdConfig
import os

if os.environ.get("ENV") == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)

# This is only being used as it sets the correct context for SQLAlchemy, which
# would require a lot of manual configuration to gain access to the database
# as it is not registered or bound to the current context.
manager = Manager(app)


@manager.command
def init_db():
    '''
    Note: not using Flask-Script as I need to run socketio below.
    '''
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.command
def populate_ontology():
    '''
    Add the initial ontology data (from pre-defined data) to the database.
    '''
    from utilities import Utils
    Utils().populate_db_from_obo_file()


@manager.command
def questions_to_sql():
    '''
    Reads the pre-defined OEQ responses, and saves them to the database.
    All questions start at the same rating (1) as they are all initially great.
    '''
    messages = messenger.Messenger().config['responses']
    for concept, questions in messages.iteritems():
        for question in questions:
            db.session.add(models.Question(
                question=question, concept=concept, rating=1))
    db.session.commit()


@manager.command
def serve():
    socketio.run(app)

if __name__ == '__main__':
    manager.run()
