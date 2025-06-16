from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import os
from client_integrations.providers import SmsProvider, EmailProvider

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    print('CONNECTING TO DB')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@"
        f"{os.environ['DB_HOST']}:5432/{os.environ['DB_NAME']}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    print('CREATING TABLES')
    with app.app_context():
        from . import models
        try:
            db.create_all()
            print('TABLES CREATED!')
        except SQLAlchemyError as e:
            print(f"Database creation error: {e}")

        app.config['sms_provider'] = SmsProvider(endpoint=os.environ['VERIZON_POST_ENDPOINT'])
        app.config['email_provider'] = EmailProvider(endpoint=os.environ['GMAIL_POST_ENDPOINT'])

        from . import routes
        from app.routes import api
        app.register_blueprint(api)

    return app
