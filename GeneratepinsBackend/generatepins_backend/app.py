from flask import Flask
from flask_restplus import Api


def create_app():
    from generatepins_backend.api_namespace import api_namespace

    application = Flask(__name__)
    api = Api(application, version='0.1', title='Generatepins Backend API',
              description='A Simple CRUD API')

    from generatepins_backend.db import db, db_config
    application.config['RESTPLUS_MASK_SWAGGER'] = False
    application.config.update(db_config)
    db.init_app(application)
    application.db = db

    api.add_namespace(api_namespace)

    return application
