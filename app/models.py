import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.extensions import db


class Meeting(db.Model):
    """
    Meeting model to store meeting minutes, action items, and decisions.
    """

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # Content
    summary = db.Column(db.Text, nullable=True)  # JSON
    action_items = db.Column(db.Text, nullable=True)  # JSON
    decisions = db.Column(db.Text, nullable=True)  # JSON

    # Analysis
    sentiment = db.Column(db.String(50), nullable=True)
    keywords = db.Column(db.Text, nullable=True)  # JSON

    original_transcript = db.Column(db.Text, nullable=False)

    def __init__(
        self,
        title,
        summary,
        action_items,
        decisions,
        original_transcript,
        sentiment="Neutral",
        keywords=None,
    ):
        self.title = title
        self.summary = json.dumps(summary) if isinstance(summary, list) else summary
        self.action_items = (
            json.dumps(action_items) if isinstance(action_items, list) else action_items
        )
        self.decisions = (
            json.dumps(decisions) if isinstance(decisions, list) else decisions
        )
        self.original_transcript = original_transcript
        self.sentiment = sentiment
        self.keywords = json.dumps(keywords if keywords else [])

    def get_summary(self):
        try:
            return json.loads(self.summary) if self.summary else []
        except:
            return []

    def get_action_items(self):
        try:
            return json.loads(self.action_items) if self.action_items else []
        except:
            return []

    def get_decisions(self):
        try:
            return json.loads(self.decisions) if self.decisions else []
        except:
            return []

    def get_keywords(self):
        try:
            return json.loads(self.keywords) if self.keywords else []
        except:
            return []
