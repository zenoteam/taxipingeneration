from flask import Flask
from flask_restplus import Api


def create_app():
    from generatepins_backend.api_namespace.api import api_namespace

    application = Flask(__name__)
    api = Api(application,
              version='1.1',
              title='Pin Generation API',
              description='Generate Otp and Pins')

    from generatepins_backend.db import db, db_config
    application.config['RESTPLUS_MASK_SWAGGER'] = False
    application.config.update(db_config)
    db.init_app(application)
    application.db = db

    api.add_namespace(api_namespace)

    return application
