from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.socketio import SocketIO

socketio = SocketIO()
db = SQLAlchemy()


def create_app(config):
    """
    Creates a flask app application factory to not bundle extensions, which
    enables multiple instances to be used with different configurations (tests).

    Args:
        config (object): The configuration object to use.

    Returns:
        app (object): The Python Flask object.
    """
    app = Flask(__name__)
    app.config.from_object(config)

    socketio.init_app(app)
    db.init_app(app)

    from app.views import main
    app.register_blueprint(main)

    return app
