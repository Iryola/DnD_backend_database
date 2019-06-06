from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")

CORS(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)

class User(db.Model):
    __tablename__ = "userAccounts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    def __init__(self, username, password):
        self.username = username
        self.password = password

class Character(db.Model):
    __tablename__ = "characters"
    id = db.Column(db.Integer, primary_key=True)
    charName = db.Column(db.String(100), nullable=False)
    race = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    health = db.Column(db.Integer, nullable=False)
    damage = db.Column(db.Integer, nullable=False)
    def __init__(self, charName, race, role, health, damage):
        self.charName = charName
        self.race = race
        self.role = role
        self.health = health
        self.damage = damage

class Monster(db.Model):
    __tablename__ = "monsters"
    id = db.Column(db.Integer, primary_key=True)
    monstName = db.Column(db.String(100), nullable=False)
    health = db.Column(db.Integer, nullable=False)
    damage = db.Column(db.Integer, nullable=False)
    def __init__(self, monstName, health, damage):
        self.monstName = monstName
        self.health = health
        self.damage = damage


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "password")

class CharacterSchema(ma.Schema):
    class Meta:
        fields = ("id", "charName", "race", "role", "health", "damage")

class MonsterSchema(ma.Schema):
    class Meta:
        fields = ("id", "monstName", "health", "damage")

user_schema = UserSchema()
users_schema = UserSchema(many=True)
character_schema = CharacterSchema()
characters_schema = CharacterSchema(many=True)
monster_schema = MonsterSchema()
monsters_schema = MonsterSchema(many=True)

def userURLVerification(submittedUsername):
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    result = result.data[0]

    dbUsername = result["username"]
    dbPassword = result["password"]

    if submittedUsername == dbUsername:
        return True
    else:
        return False


@app.route("/add-user", methods=["POST"])
def add_user():
    username = request.json["username"]
    password = request.json["password"]

    record = User(username, password)
    db.session.add(record)
    db.session.commit()
    user = User.query.get(record.id)

    return user_schema.jsonify(user)


@app.route("/login", methods=["POST"])
def login():
    submittedUsername = request.json["username"]
    submittedPassword = request.json["password"]

    all_users = User.query.all()
    result = users_schema.dump(all_users)
    result = result.data[0]

    dbUsername = result["username"]
    dbPassword = result["password"]

    if submittedUsername == dbUsername and submittedPassword == dbPassword:
        return "True"
    else:
        return "False"

@app.route("/<username>/create-character", methods=["POST"])
def generate_character(username):
    if userURLVerification(username):
        charName = request.json["charName"]
        race = request.json["race"]
        role = request.json["class"]
        health = request.json["hp"]
        damage = request.json["dmg"]

        record = Character(charName, race, role, health, damage)
        db.session.add(record)
        db.session.commit()
        character = Character.query.get(record.id)

        return character_schema.jsonify(character)
    else:
        return "You skrub, what r u doing!?!?!"

@app.route("/<username>/create-monster", methods=["POST"])
def generate_monster(username):
    if userURLVerification(username):
        monstName = request.json["monstName"]
        health = request.json["hp"]
        damage = request.json["dmg"]

        record = Monster(monstName, health, damage)
        db.session.add(record)
        db.session.commit()
        monster = Monster.query.get(record.id)

        return monster_schema.jsonify(monster)
    else:
        return "You skrub, what r u doing!?!?!"

@app.route("/<username>/delete-char/<id>", methods=["DELETE"])
def delete_char(id, username):
    if userURLVerification(username):
        record = Character.query.get(id)
        db.session.delete(record)
        db.session.commit()

        return jsonify(f'Successfuly Deleted Character #{id}')
    else:
        return "You do not have the authorization to complete that action"

@app.route("/<username>/delete-monster/<id>", methods=["DELETE"])
def delete_monster(id, username):
    if userURLVerification(username):
        record = Monster.query.get(id)
        db.session.delete(record)
        db.session.commit()

        return jsonify(f'Successfuly Deleted Monster #{id}')
    else:
        return "You do not have the authorization to complete that action"

@app.route("/all-users", methods=["GET"])
def all_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users).data

    return jsonify(result)

@app.route("/<username>/get-chars", methods=["GET"])
def get_chars(username):
    if userURLVerification(username):
        all_users = Character.query.all()
        result = characters_schema.dump(all_users).data

        return jsonify(result)
    else:
        return "No characters for you"

@app.route("/<username>/get-monsters", methods=["GET"])
def get_monsters(username):
    if userURLVerification(username):
        all_users = Monster.query.all()
        result = monsters_schema.dump(all_users).data

        return jsonify(result)
    else:
        return "No monsters for you"

if __name__ == "__main__":
    app.debug = True
    app.run()