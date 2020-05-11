from flask import Flask, Blueprint, request, jsonify, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os, requests, json
from flask import current_app as app

capi = Blueprint("capi", __name__)

cdb = SQLAlchemy()
cma = Marshmallow()

# Declaring the model.
class Car(cdb.Model):
    __tablename__ = "Car"
    carnumber = cdb.Column(cdb.String(6), primary_key = True)
    model = cdb.Column(cdb.String(20), nullable=False)
    color = cdb.Column(cdb.String(20), nullable=False)
    feature = cdb.Column(cdb.String(200), nullable=False)
    body_type = cdb.Column(cdb.String(20), nullable=False)
    seats = cdb.Column(cdb.Integer(), nullable=False)
    location = cdb.Column(cdb.String(200), nullable=False)
    cost_per_hour = cdb.Column(cdb.Float(), nullable=False)
    isAvailable = cdb.Column(cdb.Boolean(), nullable = False)
    maintenance = cdb.Column(cdb.Boolean(), default=False)
    photo = cdb.Column(cdb.String(20000), nullable=False)

class CarSchema(cma.Schema):
    # Reference: https://github.com/marshmallow-code/marshmallow/issues/377#issuecomment-261628415
    def __init__(self, strict = True, **kwargs):
        super().__init__(strict = strict, **kwargs)
    
    class Meta:
        # Fields to expose.
        fields = ("carnumber", "model", "color", "features", "body_type", "seats", "location", "cost", "img")

carSchema = CarSchema()
carsSchema = CarSchema(many = True)

# Endpoint to show all cars.
@capi.route("/car", methods = ["GET"])
def getCar():
    cars = Car.query.all()
    result = carsSchema.dump(cars)

    return jsonify(result.data)
'''
@capi.route("/car/getcarphoto/<carnumber>", methods = ["GET"])
def getCarPhoto(carnumber):
    car = Car.query.get(carnumber)
    filename = car.photo
    return send_file(filename, mimetype='image/gif')'''

def changeAvailability(self,carnumber):
    car = Car.query.filter_by(carnumber=carnumber).first()
    car.isAvailable = not(car.isAvalable)
    cdb.session.commit()

# Endpoint to show a cars by carnumber.
@capi.route("/car/<carnumber>", methods = ["GET"])
def getCarByName(carnumber):
    car = Car.query.filter_by(carnumber=carnumber).first()
    return render_template('detail.html', car = car, user = request.args['user'], disabled=False)

@capi.route("/carForBooking/<carnumber>", methods = ["GET"])
def getCarForBooking(carnumber):
    car = Car.query.filter_by(carnumber=carnumber).first()
    return redirect(car.photo)