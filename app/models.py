from app import db


class Message(db.Model):
    '''
    Read/Write the content of the message sent/received (type) from system.
    '''
    __tablename__ = 'messages'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    status = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    conversation_id = db.Column(db.String, nullable=False)


class Question(db.Model):
    '''
    Read/Write the question (OEQ, RS) sent to user, including modifying rating.
    '''
    __tablename__ = 'questions'

    id = db.Column(db.Integer, unique=True, primary_key=True)
    question = db.Column(db.String, nullable=False)
    concept = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)


class Feedback(db.Model):
    '''
    Stores the results of user feedback:
        SUS test values, and general feedback.
    '''
    __tablename__ = "feedback"

    id = db.Column(db.Integer, unique=True, primary_key=True)
    sus = db.Column(db.String, nullable=False)
    general = db.Column(db.String)


class Nodes(db.Model):
    '''
    The stores the concepts/relations from the ontology (.obo content).
    '''
    __tablename__ = 'nodes'

    id = db.Column(db.Integer, primary_key=True)
    parent = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    name = db.Column(db.String)
    parent_id = db.relationship('Nodes', foreign_keys='Nodes.parent')


class Closure(db.Model):
    '''
    Stores the hierarchy as a transitive representation.
    '''
    __tablename__ = 'closure'

    id = db.Column(db.Integer, primary_key=True)
    parent = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    child = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    depth = db.Column(db.Integer)
