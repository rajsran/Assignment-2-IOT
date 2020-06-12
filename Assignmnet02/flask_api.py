from flask import Flask, Blueprint, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os, requests, json
from flask import current_app as app

api = Blueprint("api", __name__)

db = SQLAlchemy()
ma = Marshmallow()

# Declaring the model.
class User(db.Model):
    __tablename__ = "User"
    username = db.Column(db.String(20), primary_key = True)
    email = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    dp = db.Column(db.String(100))
    # Username = db.Column(db.String(256), unique = True)

    def __init__(self, username, email, password, dp):
        self.username = username
        self.email = email
        self.password = password
        self.dp = dp

class UserSchema(ma.Schema):
    # Reference: https://github.com/marshmallow-code/marshmallow/issues/377#issuecomment-261628415
    def __init__(self, strict = True, **kwargs):
        super().__init__(strict = strict, **kwargs)
    
    class Meta:
        # Fields to expose.
        fields = ("username", "email", "password")

userSchema = UserSchema()
usersSchema = UserSchema(many = True)

# Endpoint to show all people.
@api.route("/user", methods = ["GET"])
def getPeople():
    users = User.query.all()
    result = usersSchema.dump(users)

    return jsonify(result.data)

# Endpoint to get person by id.
@api.route("/user/<username>", methods = ["GET"])
def getPerson(username):
    user = User.query.get(id)

    return userSchema.jsonify(user)

# Endpoint to create new person.
@api.route("/user", methods = ["POST"])
def addPerson():
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    newUser = User(username,email,password)

    db.session.add(newUser)
    db.session.commit()

    return userSchema.jsonify(newUser)

# Endpoint to update person.
@api.route("/user/<username>", methods = ["PUT"])
def personUpdate(username):
    user = User.query.get(username)
    password = request.json["password"]

    user.password = password

    db.session.commit()

    return userSchema.jsonify(user)

# Endpoint to delete person.
@api.route("/user/<username>", methods = ["DELETE"])
def personDelete(username):
    user = User.query.get(username)

    db.session.delete(user)
    db.session.commit()

    return userSchema.jsonify(user)



class Admin(db.Model):
    __tablename__ = "Admin"
    EmployeeID = db.Column(db.String(20), primary_key = True)
    password = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.Float)
    email = db.Column(db.String(20))

    def __init__(self, EmployeeID, password, salary):
        self.EmployeeID = EmployeeID
        self.password = password
        self.salary = salary

class AdminSchema(ma.Schema):
    # Reference: https://github.com/marshmallow-code/marshmallow/issues/377#issuecomment-261628415
    def __init__(self, strict = True, **kwargs):
        super().__init__(strict = strict, **kwargs)
    
    class Meta:
        # Fields to expose.
        fields = ("EmployeeID", "password", "salary", "email")

adminSchema = AdminSchema()
adminsSchema = AdminSchema(many = True)

# Endpoint to show all people.
@api.route("/admin", methods = ["GET"])
def getAdmin():
    admins = Admin.query.all()
    result = adminsSchema.dump(admins)

    return jsonify(result.data)

class Engineer(db.Model):
    __tablename__ = "Engineer"
    EmployeeID = db.Column(db.String(20), primary_key = True)
    password = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.Float)
    email = db.Column(db.String(20))

    def __init__(self, EmployeeID, password, salary):
        self.EmployeeID = EmployeeID
        self.password = password
        self.salary = salary

class EngineerSchema(ma.Schema):
    # Reference: https://github.com/marshmallow-code/marshmallow/issues/377#issuecomment-261628415
    def __init__(self, strict = True, **kwargs):
        super().__init__(strict = strict, **kwargs)
    
    class Meta:
        # Fields to expose.
        fields = ("EmployeeID", "password", "salary", "email")

engineerSchema = EngineerSchema()
engineersSchema = EngineerSchema(many = True)

# Endpoint to show all people.
@api.route("/engineer", methods = ["GET"])
def getEngineer():
    engineers = Engineer.query.all()
    result = engineersSchema.dump(engineers)

    return jsonify(result.data)

class Manager(db.Model):
    __tablename__ = "Manager"
    EmployeeID = db.Column(db.String(20), primary_key = True)
    password = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.Float)
    email = db.Column(db.String(20))

    def __init__(self, EmployeeID, password, salary):
        self.EmployeeID = EmployeeID
        self.password = password
        self.salary = salary

class ManagerSchema(ma.Schema):
    # Reference: https://github.com/marshmallow-code/marshmallow/issues/377#issuecomment-261628415
    def __init__(self, strict = True, **kwargs):
        super().__init__(strict = strict, **kwargs)
    
    class Meta:
        # Fields to expose.
        fields = ("EmployeeID", "password", "salary", "email")

managerSchema = ManagerSchema()
managersSchema = ManagerSchema(many = True)

# Endpoint to show all people.
@api.route("/manager", methods = ["GET"])
def getManager():
    managers = Manager.query.all()
    result = managersSchema.dump(managers)

    return jsonify(result.data)

