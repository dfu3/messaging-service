from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@"
        f"{os.environ['DB_HOST']}:5432/{os.environ['DB_NAME']}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        from . import models
        try:
            db.create_all()
        except SQLAlchemyError as e:
            app.logger.error(f"Database creation error: {e}")

    from . import routes

    return app
