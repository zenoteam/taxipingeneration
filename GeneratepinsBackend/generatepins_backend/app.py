import os
from pathlib import Path
from flask import Flask
from flask_restplus import Api


dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
loc = dir_path / 'templates/'


def create_app():
    from generatepins_backend.api_namespace import api_namespace

    application = Flask(__name__, template_folder=loc)
    api = Api(application, version='0.1', title='Generatepins Backend API',
              description='A Simple CRUD API')

    from generatepins_backend.db import db, db_config
    application.config['RESTPLUS_MASK_SWAGGER'] = False
    application.config.update(db_config)
    db.init_app(application)
    application.db = db

    from generatepins_backend.message import mail, mail_config
    application.config.update(mail_config)
    mail.init_app(application)

    api.add_namespace(api_namespace)

    return application
