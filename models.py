# models.py
from app import db

class AdReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clinic_name = db.Column(db.String(50), nullable=False)
    adspend = db.Column(db.Float, nullable=False)
    cpl = db.Column(db.Float, nullable=False)
    leads = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    from_date = db.Column(db.DateTime, nullable=False)
    until_date = db.Column(db.DateTime, nullable=False)
