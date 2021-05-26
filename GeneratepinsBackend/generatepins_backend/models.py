from sqlalchemy import func
from generatepins_backend.db import db


class PinGenModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    phone_number = db.Column(db.String(250))
    pin = db.Column(db.String(50))
    verified = db.Column(db.Boolean(), default=False)
    type = db.Column(db.Integer())
    count = db.Column(db.Integer(), default=1)
    expiry_time = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime, server_default=func.now())
