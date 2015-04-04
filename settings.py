import os


class Config(object):
    """
    The shared configuration settings for the flask app.
    """
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    DATA_FOLER = PROJECT_ROOT + '/data/'
    ONTOLOGY = DATA_FOLER + 'structure.obo'


class ProdConfig(Config):
    """
    Setup the production configuration for the flask app.

    Args:
        Config (object): Inherit the default shared configuration settings.
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', None)


class DevConfig(Config):
    """
    Setup the development configuration for the flask app.

    Args:
        Config (object): Inherit the default shared configuration settings.
    """
    DEBUG = True
    LOCAL_DB_PATH = os.path.join(Config.PROJECT_ROOT, 'dev.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(LOCAL_DB_PATH)
