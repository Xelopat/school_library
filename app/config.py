import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('lib.db') or \
                              'sqlite:///' + os.path.join(basedir, 'lib.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
