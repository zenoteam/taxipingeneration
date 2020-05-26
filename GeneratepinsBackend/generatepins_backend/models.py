from sqlalchemy import func
from generatepins_backend.db import db


class GeneratepinModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    pin = db.Column(db.String(50))
    expiry_time = db.Column(db.DateTime, server_default=func.now())
