from app import db


class Message(db.Model):
    '''
    Read/Write the content of the message sent/received (type) from system.
    '''
    __tablename__ = 'messages'

    # Initially, I was also going to store an ID for each conversation, to allow
    # analysis of each conversation. That is outside the current project scope.
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    status = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)

    def __init__(self, _status, _content):
        self.status = _status  # Used to differentiate between sent/received.
        self.content = _content

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
