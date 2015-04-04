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

    def __init__(self, _status, _content, _conversation_id):
        self.status = _status  # differentiate between sent/received.
        self.content = _content
        self.conversation_id = str(_conversation_id)  # diff questions sent.

    def __repr__(self):
        return 'Message & type: %r, -> %r.' % (self.content, self.status)


class Question(db.Model):
    '''
    Read/Write the question (OEQ, RS) sent to user, including modifying rating.
    '''
    __tablename__ = 'questions'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    question = db.Column(db.String, nullable=False)
    concept = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __init__(self, _question, _concept, _rating):
        self.question = _question
        self.concept = _concept
        self.rating = _rating

    def __repr__(self):
        return 'Concept: question -> rating: %r: %r : %r' \
            % (self.concept, self.question, self.rating)


class Feedback(db.Model):
    '''
    Stores the results of user feedback:
        SUS test values, and general feedback.
    '''
    __tablename__ = "feedback"

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    sus = db.Column(db.String, nullable=False)
    general = db.Column(db.String)


class Nodes(db.Model):
    __tablename__ = 'nodes'

    id = db.Column(db.Integer, primary_key=True)
    parent = db.Column(db.Integer, db.ForeignKey('nodes.id'), nullable=False)
    name = db.Column(db.String)
    parent_id = db.relationship('Nodes', foreign_keys='Nodes.parent')


class Closure(db.Model):
    __tablename__ = 'closure'

    id = db.Column(db.Integer, primary_key=True)
    parent = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    child = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    depth = db.Column(db.Integer)
