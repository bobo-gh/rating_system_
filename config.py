import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'your_secret_key'  # 可自行更改
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'ratings.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False