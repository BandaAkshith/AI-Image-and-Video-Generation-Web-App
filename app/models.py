from . import db  # Import the db instance from __init__.py
from datetime import datetime


class Content(db.Model):
    __tablename__ = 'content'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    video_paths = db.Column(db.Text)
    image_paths = db.Column(db.Text)
    status = db.Column(db.String, default="Processing")
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
