import logging
from logging.handlers import SMTPHandler

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_app.config import Config

# App management
app = Flask(__name__)
app.config.from_object(Config)

# DB management
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Login management
login = LoginManager(app)
login.login_view = 'login'

# Email management
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        secure = None

        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (
                app.config['MAIL_USERNAME'],
                app.config['MAIL_PASSWORD']
            )

        if app.config['MAIL_USE_TLS']:
            secure = ()

        mail_handler = SMTPHandler(
            mailhost=(
                app.config['MAIL_SERVER'],
                app.config['MAIL_PORT']
            ),
            fromaddr=f"no-reply@{app.config['MAIL_SERVER']}",
            toaddrs=app.config['ADMINS'],
            subject='Demo flask app failure',
            credentials=auth,
            secure=secure
        )

        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

from flask_app.app import routes, models, errors

