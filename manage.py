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
    Create initial database tables.
    '''
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.command
def populate_ontology():
    '''
    Add the initial ontology data to the database.
    '''
    from utilities import Utils
    Utils().populate_db_from_obo_file()


@manager.command
def update_ontology():
    '''
    Manually assign children to parent terms.
    '''
    from utilities import Utils
    Utils().assign_terms_to_obo_file()


@manager.command
def questions_to_sql():
    '''
    Saves pre-defined responses to database with rating 1.
    '''
    messages = messenger.Messenger().config['responses']
    for concept, questions in messages.iteritems():
        for question in questions:
            db.session.add(models.Question(
                question=question, concept=concept, rating=1))
    db.session.commit()


@manager.command
def runserver():
    '''
    Required to run socketio rather than default manager.
    '''
    socketio.run(app)

if __name__ == '__main__':
    manager.run()
