
from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_marshmallow import Marshmallow
import os, requests, json
from forms import RegistrationForm, LoginForm, BookingForm, FilterForm
#from users import User
from flask_api import api, db, User
from car_api import capi,cdb,Car
from booking_api import bapi, bdb, Booking
from datetime import date, datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
basedir = os.path.abspath(os.path.dirname(__file__))

HOST = "34.87.232.0"
USER = "root"
PASSWORD = "123456"
DATABASE = "People"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://{}:{}@{}/{}".format(USER, PASSWORD, HOST, DATABASE)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db.init_app(app)
cdb.init_app(app)

app.register_blueprint(api)
app.register_blueprint(capi)

@app.route("/", methods=['GET', 'POST'])
def home():
    form = LoginForm()
    if form.validate_on_submit()==True:
        user = User.query.filter_by(email=form.email.data).first()
        if user and form.password.data==user.password:
            return redirect(url_for('main_page', user = user.username))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit()==True:
        flash('Account created!', 'success')
        user =  User(form.username.data, form.email.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route("/booking", methods=['GET', 'POST'])
def booking():
    form = BookingForm()
    form.carnumber.data = request.args['carnumber']
    form.user.data = request.args['user']
    #form.start_date.data=date.today()
    #form.end_date.data=date.today()
    form.number_of_days.data='0'
    form.cost.data='0'
    
    
    if ((form.validate_on_submit()==True)):
        form.start_date.data=form.start_date.data
        form.end_date.data=form.end_date.data
        form.number_of_days.data = form.setnod(form.start_date,form.end_date).days+1
        car = Car.query.filter_by(carnumber=form.carnumber.data).first()
        price = car.cost_per_hour
        form.cost.data = form.setcost(form.number_of_days, price)
        flash('Booking confirmed!', 'success')
        bid = form.carnumber.data + datetime.strftime(form.start_date.data, '%m/%d/%Y')
        booking =  Booking(booking_id = bid,carnumber = form.carnumber.data,user = form.user.data,start_date = form.start_date.data, end_date = form.end_date.data,start_location =  car.location, end_location = None, number_of_days = form.number_of_days.data, cost = form.cost.data)
        bdb.session.add(booking)
        car.isAvailable = False
        cdb.session.commit()
        bdb.session.commit()
        print("returning true")
        return render_template('booking.html', form=form, user = request.args['user'], disabled='true')    
       
    return render_template('booking.html', form=form, user = request.args['user'], disabled = 'false')

@app.route("/main_page", methods=['GET', 'POST'])
def main_page():
    form = FilterForm()
    cars = Car.query.all()
    if form.validate_on_submit()==True:
        cars = Car.query.all().first()
        return render_template('main.html', cars=cars, user = request.args['user'])
    return render_template('main.html', cars=cars, user = request.args['user'])

@app.route("/cancelBooking", methods=['GET', 'POST'])
def cancelBooking():
    booking = Booking.query.filter_by(booking_id=request.args['booking_id']).first()
    booking.end_date = None
    booking.cost=0
    booking.number_of_days = 0
    booking.end_location = booking.start_location
    bdb.session.commit()
    car = Car.query.filter_by(carnumber=booking.carnumber).first()
    car.isAvailable = True
    cdb.session.commit()
    cars = Car.query.all()
    return render_template('main.html', cars = cars, user = request.args['user'])
    
@app.route("/closeBooking", methods=['GET', 'POST'])
def closeBooking():
    booking = Booking.query.filter_by(booking_id=request.args['booking_id']).first()
    booking.end_date = date.today()
    booking.number_of_days = (booking.end_date-booking.start_date).days+1
    booking.end_location = "melbourne"
    bdb.session.commit()
    car = Car.query.filter_by(carnumber=booking.carnumber).first()
    car.isAvailable = True
    car.location = booking.end_location
    cdb.session.commit()
    booking.cost= car.cost_per_hour*booking.number_of_days
    bdb.session.commit()
    cars = Car.query.all()
    return render_template('main.html', cars = cars, user = request.args['user'])

@app.route("/reportIssue", methods=['GET', 'POST'])
def reportIssue():
    booking = Booking.query.filter_by(booking_id=request.args['booking_id']).first()
    booking.end_date = date.today()
    booking.number_of_days = (booking.end_date-booking.start_date).days+1
    booking.end_location = "melbourne"
    bdb.session.commit()
    car = Car.query.filter_by(carnumber=booking.carnumber).first()
    car.isAvailable = True
    car.maintenance = True
    car.location = booking.end_location
    cdb.session.commit()
    booking.cost= car.cost_per_hour*booking.number_of_days
    bdb.session.commit()
    cars = Car.query.all()
    return render_template('main.html', cars = cars, user = request.args['user'])
        

@app.route("/prev_bookings", methods=['GET', 'POST'])
def prev_bookings():
    bookings = Booking.query.filter(Booking.user==request.args['user']).filter(or_(Booking.end_date<=date.today(),Booking.end_date==None))
    return render_template('oldbookings.html', bookings=bookings, user = request.args['user'])

@app.route("/curr_bookings", methods=['GET', 'POST'])
def curr_bookings():
    bookings = Booking.query.filter(Booking.user==request.args['user'],Booking.end_date>=date.today())
    
    return render_template('currbookings.html', bookings=bookings, user = request.args['user'])


if (__name__) == '__main__':
    app.run(debug=True)


