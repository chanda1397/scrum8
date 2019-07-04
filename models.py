from api import db


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean, default=False)


class Event(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    title = db.Column(db.String(50))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    venue = db.Column(db.String(50))
    flyer = db.Column(db.Text)
    cost = db.Column(db.Integer)
    creator = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    public = db.Column(db.Boolean, default=False)


class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.user_id'), nullable=True)


class Rate(db.Model):
    rate_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
