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
    from app import database
    database.Database().create_tables()
    # creating afterwards as the database class is more likely to throw errors.
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.command
def populate_ontology():
    '''
    Add the initial ontology data (from pre-defined data) to the database.
    '''
    __populate_from_obo()


def __populate_from_obo():
    '''
    Inserts concepts/terms into the database.

    Moreover, the transitive closure table is also updated upon insertion
    of an element to ensure it's retrievable later.

    Note: based on - http://blog.adimian.com/2014/10/cte-and-closure-tables/
    '''
    from utils import obo
    # Note: structure.obo MUST contain the initial concepts.
    path = DevConfig.DATA_FOLER + 'structure.obo'
    obo_content = [i for i in obo.Parser(path)]

    known_ids = [r[0] for r in
                 db.engine.execute('SELECT id FROM nodes').fetchall()]

    for i in obo_content:
        _id = int(str(i.tags['id'][0]).split(':')[1])
        # The root element does not have a parent. Assign it a zero.
        _pid = (int(str(i.tags['is_a'][0]).split(':')[1])
                if 'is_a' in str(i) else 0)
        _name = str(i.tags['name'][0])
        # Only add NEW terms to the database.
        if _id not in known_ids:
            # Add ontological term to node table.
            last_id = db.engine.execute('INSERT INTO nodes VALUES (?, ?, ?)',
                                        (_id, _pid, _name)).lastrowid
            # Collect ancestor of parent, and insert into closure table.
            values = db.engine.execute(
                'SELECT parent, ? as child, depth+1 FROM closure '
                'WHERE child = ?', (_id, _pid)).fetchall()
            stm = 'INSERT INTO closure (parent, child, depth) VALUES (?, ?, ?)'
            for i in values:
                db.engine.execute(stm, i)
            db.engine.execute(stm, (last_id, last_id, 0))
    db.session.commit()


@manager.command
def questions_to_sql():
    '''
    Reads the pre-defined OEQ responses, and saves them to the database.
    '''
    messages = messenger.Messenger().config['responses']
    for concept, questions in messages.iteritems():
        for question in questions:
            db.session.add(models.Question(question, concept, 1))
    db.session.commit()


@manager.command
def serve():
    socketio.run(app)

if __name__ == '__main__':
    manager.run()
