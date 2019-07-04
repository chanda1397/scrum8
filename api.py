from models import *
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
import jwt
import datetime
app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
CORS(app)


UPLOAD_FOLDER = "/Users/chanderpaulmartin/Desktop/scrum7/app/scrum7client/public/img"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-auth-token' in request.headers:
            token = request.headers['x-auth-token']

        if not token:
            return make_response("Token is required", 401)

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])

            current_user = User.query.filter_by(
                public_id=data['id']).first()

        except:
            return make_response("Token is invalid", 401)

        return f(current_user, *args, **kwargs)

    return decorated


@app.route("/api/auth", methods=["GET"])
@token_required
def get_user(current_user):
    user_data = {
        "name": current_user.name,
        "email": current_user.email,
        "public_id": current_user.public_id,
        "id": current_user.user_id,
        "admin": current_user.admin
    }

    return jsonify(user_data)


@app.route("/api/users/<user_id>", methods=["GET"])
def get_user_by_id(user_id):
    user = User.query.filter_by(user_id=user_id)

    if not user:
        return make_response("User not found", 404)
    user_data = {
        "name": user.name,
        "email": user.email,
        "public_id": user.public_id,
        "id": user.user_id,
        "admin": user.admin
    }

    return jsonify(user_data)


@app.route("/api/users/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        check = User.query.filter_by(email=data['email']).first()

        if not check:

            hashed_password = generate_password_hash(
                data['password'], method='sha256')
            public_id = str(uuid.uuid4())

            user = User(public_id=public_id, name=data['name'],
                        password=hashed_password, email=data['email'])
            db.session.add(user)
            db.session.commit()

            return jsonify({"message": "User successfully register"})
        else:
            return jsonify({"message": "User already exists or email is already taken"})

    except Exception as e:
        print(e)
        return make_response("Server error", 500)


@app.route("/api/users", methods=["GET"])
def get_all_users():

    try:

        users = User.query.all()

        output = []
        for user in users:
            user_data = {
                "name": user.name,
                "public_id": user.public_id,
                "email": user.email,
                "admin": user.admin
            }
            output.append(user_data)
        return jsonify({"users": output})
    except Exception as e:
        print(e)
        return make_response("Server error", 500)


@app.route("/api/auth/login", methods=['POST'])
def login():
    try:
        data = request.get_json()

        user = User.query.filter_by(email=data['email']).first()

        if not user:
            return make_response('Invalid credentials', 401)

        if check_password_hash(user.password, data['password']):
            token = jwt.encode({'id': user.public_id},
                               app.config['SECRET_KEY'])
            return jsonify({"token": token.decode('utf-8')})
        else:
            return make_response('Invalid credentials', 401)
    except Exception as e:
        print(e)
        return make_response('Server error', 500)


@app.route("/api/events", methods=['GET'])
def get_all_events():

    try:
        events = Event.query.all()

        output = []

        for event in events:

            event_data = {
                "id": event.event_id,
                "name": event.name,
                "description": event.description,
                "category": event.category,
                "title": event.title,
                "start_date": event.start_date,
                "end_date": event.end_date,
                "venue": event.venue,
                "flyer": event.flyer,
                "creator": event.creator,
                "public": event.public,
                "cost": event.cost
            }
            output.append(event_data)
        return jsonify({'events': output})

    except Exception as e:
        print(e)
        return make_response('Server error', 500)


@app.route("/api/events", methods=['POST'])
@token_required
def create_event(current_user):
    try:
        data = request.get_json()
        date = data['start_date'].split("-")
        start_date = datetime.datetime(
            int(date[0]), int(date[1]), int(date[2]))
        date = data['end_date'].split("-")
        end_date = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))
        cost = int(data["cost"])

        # file = request.files['flyer']

        # filename = ""
        # if file:
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        event = Event(name=data['name'], description=data['description'], category=data['category'], title=data['title'],
                      start_date=start_date, cost=cost, end_date=end_date, venue=data['venue'], flyer=data['flyer'], creator=current_user.user_id)

        db.session.add(event)
        db.session.commit()
        return jsonify({"message": "Event created"})
    except Exception as e:
        print(e)
        return make_response('Server error', 500)


@app.route("/api/events/<event_id>", methods=['PUT'])
@token_required
def update_event(current_user, event_id):
    try:
        event = Event.query.filter_by(event_id=event_id).first()

        if not event:
            return jsonify({"message": "Event not found"}), 404

        if event.creator != current_user.user_id and not current_user.admin:
            return jsonify({"message": "Unauthorized"}), 401

        data = request.get_json()

        for k in data:
            if k == 'name':
                event.name = data['name']
            if k == 'category':
                event.category = data['category']
            if k == 'flyer':
                event.flyer = data['flyer']
            if k == 'venue':
                event.venue = data['venue']
            if k == 'description':
                event.description = data['description']
            if k == 'title':
                event.title = data['title']
            if k == 'public':
                event.public = True

        db.session.commit()
        return jsonify({"message": "Event updated"})

    except Exception as e:
        print(e)
        make_response('Server error', 500)


@app.route("/api/events/<event_id>", methods=["DELETE"])
@token_required
def delete_event(current_user, event_id):
    try:
        event = Event.query.filter_by(event_id=event_id).first()

        if not event:
            return jsonify({"message": "Event not found"}), 404

        if event.creator != current_user.user_id:
            return jsonify({"message": "Unauthorized"}), 401

        db.session.delete(event)
        db.session.commit()
        return jsonify({"message": "Event deleted"})

    except Exception as e:
        print(e)
        make_response('Server error', 500)


@app.route("/api/events/<event_id>/comments/<user_id>", methods=['POST'])
def make_comment(event_id, user_id):
    try:
        data = request.get_json()
        event = Event.query.filter_by(event_id=event_id).first()

        if not event:
            return jsonify({"message": "Event not found"}), 404

        comment = Comment(text=data["text"],
                          event_id=event_id, user_id=user_id)

        db.session.add(comment)
        db.session.commit()

        return jsonify({"message": "Comment made"})

    except Exception as e:
        print(e)
        return make_response('Server error', 500)


@app.route("/api/events/<event_id>/comments", methods=['POST'])
def make_comment_annoymous(event_id):
    try:
        data = request.get_json()
        event = Event.query.filter_by(event_id=event_id).first()

        if not event:
            return jsonify({"message": "Event not found"}), 404

        comment = Comment(text=data["text"],
                          event_id=event_id)

        db.session.add(comment)
        db.session.commit()

        return jsonify({"message": "Comment made"})

    except Exception as e:
        print(e)
        print("this function")
        return make_response('Server error', 500)


@app.route("/api/events/<event_id>/comments", methods=["GET"])
def get_comments(event_id):

    try:
        event = Event.query.filter_by(event_id=event_id).first()
        if not event:
            return jsonify({"message": "Event not found"}), 404

        comments = Comment.query.filter_by(event_id=event_id)

        output = []
        for comment in comments:
            username = ""

            user = User.query.filter_by(user_id=comment.user_id).first()

            if not user:
                username = "Annoymous"
            else:
                username = user.name
            comment_data = {
                "comment_id": comment.comment_id,
                "text": comment.text,
                "event_id": comment.event_id,
                "username": username
            }
            output.append(comment_data)
        return jsonify({"comments": output})
    except Exception as e:
        print(e)
        make_response('Server error', 500)


@app.route("/api/events/<event_id>/rates", methods=['POST'])
def make_rate(event_id):
    try:
        data = request.get_json()
        event = Event.query.filter_by(event_id=event_id).first()

        if not event:
            return jsonify({"message": "Event not found"}), 404

        rate = Rate(value=data["value"], event_id=event_id)

        db.session.add(rate)
        db.session.commit()

        return jsonify({"message": "Rate made"})

    except Exception as e:
        print(e)
        return make_response('Server error', 500)


@app.route("/api/events/<event_id>/rates", methods=["GET"])
def get_rates(event_id):

    try:
        event = Event.query.filter_by(event_id=event_id).first()
        if not event:
            return jsonify({"message": "Event not found"}), 404

        rates = Rate.query.filter_by(event_id=event_id)

        output = []
        for rate in rates:
            rate_data = {
                "rate_id": rate.rate_id,
                "text": rate.value,
                "event_id": rate.event_id
            }
            output.append(rate_data)
        return jsonify({"rates": output})
    except Exception as e:
        print(e)
        make_response('Server error', 500)


if __name__ == '__main__':
    app.run(port=5500, debug=True)
