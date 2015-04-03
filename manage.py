from app import create_app, socketio, messenger, db, models
from settings import DevConfig, ProdConfig
import os

if os.environ.get("ENV") == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)


def init_db():
    '''
    Note: not using Flask-Script as I need to run socketio below.
    '''
    from app import database
    database.Database().create_tables()
    # creating afterwards as the database class is more likely to throw errors.
    db.drop_all()
    db.create_all()
    db.session.commit()


def populate_ontology():
    '''
    Add the initial ontology data (from pre-defined data) to the database.
    '''
    from utils import obo_to_sql
    obo_to_sql.populate_from_obo()


def questions_to_sql():
    '''
    Reads the pre-defined OEQ responses, and saves them to the database.
    '''
    messages = messenger.Messenger().config['responses']
    for concept, questions in messages.iteritems():
        for question in questions:
            db.session.add(models.Question(question, concept, 1))
    db.session.commit()


if __name__ == '__main__':
    socketio.run(app)
