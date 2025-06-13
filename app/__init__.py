from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    print('CONNECTING TO DB')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@"
        f"{os.environ['DB_HOST']}:5432/{os.environ['DB_NAME']}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    print(app.config['SQLALCHEMY_DATABASE_URI'])

    db.init_app(app)

    print('CREATING TABLES')
    with app.app_context():
        from . import models
        try:
            db.create_all()
            print('TABLES CREATED!')
        except SQLAlchemyError as e:
            print(f"Database creation error: {e}")

        from . import routes

    return app
