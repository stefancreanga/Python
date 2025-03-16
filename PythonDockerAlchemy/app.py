# Small Python and Docker project application.
# It's an SQLAlchemy very simple database with
# input validation check using Marshmallow and
# request limit using flask-limiter

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from sqlalchemy.exc import IntegrityError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

app = Flask(__name__, template_folder='templates')

# Set up the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///data.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initializing the database
db = SQLAlchemy(app)

# Initializing Marshmallow
ma = Marshmallow(app)

# Initializing the Flask-Limiter
limiter = Limiter(get_remote_address, app=app)

# Defining the table for storing users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"

# Defining the user schema for validation
class UserSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)

user_schema = UserSchema()

# Setting the rate limit to 5 requests per minute per IP
@app.route("/", methods=["GET"])
@limiter.limit("5 per minute")
def home():
    return render_template("index.html")

@app.route("/users", methods=["GET"])
@limiter.limit("5 per minute")
def get_users():
    users = User.query.all()
    return jsonify([{ "id": user.id, "name": user.name, "email": user.email } for user in users])

@app.route("/user", methods=["POST"])
@limiter.limit("5 per minute")
def add_user():
    try:
        data = user_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    new_user = User(name=data["name"], email=data["email"])
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User added successfully!"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Email already exists!"}), 400

@app.route("/user/<int:id>", methods=["PUT"])
@limiter.limit("5 per minute")
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "User not found!"}), 404
    
    try:
        data = user_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user.name = data["name"]
    user.email = data["email"]
    db.session.commit()
    return jsonify({"message": "User updated successfully!"})

@app.route("/user/<int:id>", methods=["DELETE"])
@limiter.limit("5 per minute")
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "User not found!"}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully!"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
