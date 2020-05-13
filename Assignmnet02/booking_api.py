from flask import Flask, Blueprint, request, jsonify, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os, requests, json
from flask import current_app as app
from car_api import Car, capi, cdb
from add_event import CalendarEvent

from datetime import datetime
from datetime import timedelta

bapi = Blueprint("bapi", __name__)

bdb = SQLAlchemy()
bma = Marshmallow()

# Declaring the model.
class Booking(bdb.Model):
    __tablename__ = "Booking"
    booking_id = bdb.Column(bdb.String(50), primary_key = True)
    carnumber = bdb.Column(bdb.String(6), nullable = False)
    user = bdb.Column(bdb.String(200), nullable = False)
    start_date = bdb.Column(bdb.Date, nullable=False)
    end_date = bdb.Column(bdb.Date)
    start_location = bdb.Column(bdb.String(200), nullable=False)
    end_location = bdb.Column(bdb.String(100))
    number_of_days = bdb.Column(bdb.Integer(), nullable=False)
    status = bdb.Column(bdb.Boolean, default=True)
    cost = bdb.Column(bdb.Float(), nullable=False)
    event_id = bdb.Column(bdb.String(200), default=None)
    
    def addToCalendar(self, service):
        cal = CalendarEvent(self.start_date, self.booking_id, self.start_location)
        eid = cal.addToCalendar(self.carnumber, service)
        return eid
 
    def removeFromCalendar(self, service):
        cal = CalendarEvent(self.start_date, self.booking_id, self.start_location)
        cal.removeFromCalendar(self.event_id, service)
        
class BookingSchema(bma.Schema):
    # Reference: https://github.com/marshmallow-code/marshmallow/issues/377#issuecomment-261628415
    def __init__(self, strict = True, **kwargs):
        super().__init__(strict = strict, **kwargs)
    
    class Meta:
        # Fields to expose.
        fields = ("booking_id", "carnumber", "user", "start_date", "end_date", "start_location", "end_location", "number_of_days", "cost")

bookingSchema = BookingSchema()
bookingsSchema = BookingSchema(many = True)

# Endpoint to show all bookings.
@bapi.route("/booking", methods = ["GET"])
def getBooking():
    bookings = Booking.query.all()
    result = bookingsSchema.dump(bookings)

    return jsonify(result.data)
'''
@capi.route("/car/getcarphoto/<carnumber>", methods = ["GET"])
def getCarPhoto(carnumber):
    car = Car.query.get(carnumber)
    filename = car.photo
    return send_file(filename, mimetype='image/gif')'''

# Endpoint to show a cars by carnumber.
@bapi.route("/booking/<booking_id>", methods = ["GET"])
def getBookingById(bookin_id, service):
    booking = Booking.query.filter_by(bookin_id=booking_id).first()
    result = bookingsSchema.dump(bookings)
    return jsonify(result.data)

# Endpoint to show a cars by carnumber.
@bapi.route("/booking/<booking_id>", methods = ["GET"])
def getBookingByName(booking_id, service):
    booking = Booking.query.filter_by(booking_id=booking_id).first()
    #return render_template('detail.html', car = car, user = request.args['user'])
    

