from __future__ import print_function
from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_
from flask_marshmallow import Marshmallow
import os, requests, json, sqlite3
from forms import RegistrationForm, AdminRegistrationForm, AdminUpdateForm, LoginForm, BookingForm, FilterForm, SearchForm, AdminAddCarForm
from flask_bcrypt import Bcrypt
#from users import User
from flask_api import api, db, User, Admin, Engineer, Manager
from car_api import capi,cdb,Car
from booking_api import bapi, bdb, Booking
from issue_api import iapi, idb, Issue
from datetime import date, datetime
import googlemaps

from datetime import datetime
from datetime import timedelta
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import logging
import os
import cloudstorage as gcs
from gcloud import storage
from google.cloud import storage

from pushbullet import Pushbullet

pb = Pushbullet('o.V6LChFjuMwBnctjCgBDCPQaSm67dJxTc')

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

bcrypt = Bcrypt(app)


@app.route("/", methods=['GET', 'POST'])
def home():
    
    form = LoginForm()
    if form.validate_on_submit()==True:
        user = User.query.filter_by(email=form.email.data).first()
        admin = Admin.query.filter_by(EmployeeID=form.email.data).first()
        engineer = Engineer.query.filter_by(EmployeeID=form.email.data).first()
        manager = Manager.query.filter_by(EmployeeID=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            
            form = FilterForm()
            return redirect(url_for('main_page', form = form, user = user.username))
    
        elif admin and (admin.password == form.password.data):
            
            form = FilterForm()
            return redirect(url_for('admin_main_page', form = form, user = admin.EmployeeID))
        
        elif engineer and bcrypt.check_password_hash(engineer.password, form.password.data):
            return redirect(url_for('engineer_main_page', user = engineer.EmployeeID))
       
        elif manager and bcrypt.check_password_hash(manager.password, form.password.data):
            return redirect(url_for('manager_main_page', user = manager.EmployeeID))
        
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit()==True:
        flash('Account created!', 'success')
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if (form.dp.data):
            client = storage.Client()
            bucket = client.get_bucket('a2iot-carshare.appspot.com')
            blob = bucket.blob('dp_'+form.username.data+'.jpg')
            with open('/home/pi/Desktop/'+form.dp.data, "rb") as my_file:
                blob.upload_from_file(my_file)
            dp = "https://storage.cloud.google.com/a2iot-carshare.appspot.com/dp_"+form.username.data+".jpg"
        else:
            dp=None
        user =  User(username = form.username.data, email = form.email.data, password = hashed_password, dp = dp)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route("/booking", methods=['GET', 'POST'])
def booking():
    form = BookingForm()
    form.carnumber.data = request.args['carnumber']
    form.user.data = request.args['user']
    form.number_of_days.data='0'
    form.cost.data='0'
    service = build("calendar", "v3", http=Http())
    
    if ((form.validate_on_submit()==True)):
        form.start_date.data=form.start_date.data
        form.end_date.data=form.end_date.data
        form.number_of_days.data = form.setnod(form.start_date,form.end_date).days+1
        car = Car.query.filter_by(carnumber=form.carnumber.data).first()
        price = car.cost_per_hour
        form.cost.data = form.setcost(form.number_of_days, price)
        flash('Booking confirmed!', 'success')
        bid = form.carnumber.data + datetime.strftime(form.start_date.data, '%m/%d/%Y')
        booking =  Booking(booking_id = bid,carnumber = form.carnumber.data,user = form.user.data,start_date = form.start_date.data, end_date = form.end_date.data,start_location =  car.location, end_location = None, number_of_days = form.number_of_days.data,status=True, cost = form.cost.data, event_id = None)
        bdb.session.add(booking)
        eid = booking.addToCalendar(service)
        eid = eid.split("?eid=",1)
        eveid = eid[1]
        booking.event_id=eveid
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
    if request.method=='POST':
        
        if (form.search.data==None or form.search.data=='' or form.search.data==[]):
            cars1 = Car.query.all()
        else:
            cars1 = Car.query.filter(or_(Car.carnumber==form.search.data, Car.model==form.search.data))
        
        if (form.available.data=="available cars only"):
            cars2 = Car.query.filter(and_(Car.isAvailable==True, Car.maintenance==False))
        elif (form.available.data=="all cars"):
            cars2 = Car.query.all()
        else:
            cars2 = Car.query.all()

        
        if (form.cost_below.data==None or form.cost_below.data=='' or form.cost_below.data==[]):
            cars3 = Car.query.all()
        else:
            cars3 = Car.query.filter(Car.cost_per_hour<=form.cost_below.data)
        
        if (form.body.data==None or form.body.data=='' or form.body.data==[]):
            cars4= Car.query.all()
        else:
            if (form.body.data=="SUV"):
                cars4 = Car.query.filter(Car.body_type=="suv")
            elif (form.body.data=="sedan"):
                cars4 = Car.query.filter(Car.body_type=="sedan")
            else:
                cars4 = Car.query.filter(Car.body_type=="hatch")
         
        print(list(set(cars1) & set(cars2) & set(cars3) & set(cars4)))
        cars = list(set(cars1) & set(cars2) & set(cars3) & set(cars4))
        if (cars is None or cars==None or len(cars)==0):
            flash('No results found, please re-edit filters!', 'danger')
            cars = Car.query.all()
        return render_template('main.html', form = form, cars=cars, user = request.args['user'])
    return render_template('main.html', form = form, cars=cars, user = request.args['user'])

@app.route("/cancelBooking", methods=['GET', 'POST'])
def cancelBooking():
    service = None
    booking = Booking.query.filter_by(booking_id=request.args['booking_id']).first()
    booking.end_date = booking.start_date
    booking.cost=0
    booking.number_of_days = 0
    booking.status = False
    booking.end_location = booking.start_location
    booking.removeFromCalendar(service)
    bdb.session.commit()
    car = Car.query.filter_by(carnumber=booking.carnumber).first()
    car.isAvailable = True
    cdb.session.commit()
    cars = Car.query.all()
    form = FilterForm()
    return render_template('main.html', form=form, cars = cars, user = request.args['user'])
    
@app.route("/closeBooking", methods=['GET', 'POST'])
def closeBooking():
    service = None
    booking = Booking.query.filter_by(booking_id=request.args['booking_id']).first()
    booking.end_date = date.today()
    booking.number_of_days = (booking.end_date-booking.start_date).days+1
    booking.end_location = "melbourne"
    booking.status = False
    booking.removeFromCalendar(service)
    bdb.session.commit()
    car = Car.query.filter_by(carnumber=booking.carnumber).first()
    car.isAvailable = True
    car.location = booking.end_location
    cdb.session.commit()
    booking.cost= car.cost_per_hour*booking.number_of_days
    bdb.session.commit()
    cars = Car.query.all()
    form = FilterForm()
    return render_template('main.html', form = form, cars = cars, user = request.args['user'])

@app.route("/reportIssue", methods=['GET', 'POST'])
def reportIssue():
    service = build("calendar", "v3", http=Http())
    booking = Booking.query.filter_by(booking_id=request.args['booking_id']).first()
    if (date.today()>booking.start_date):
        booking.end_date = date.today()
        booking.number_of_days = (booking.end_date-booking.start_date).days+1
        booking.cost= car.cost_per_hour*booking.number_of_days
        booking.end_location = "melbourne"
    else:
        booking.end_date = booking.start_date
        booking.cost=0
        booking.number_of_days = 0
        booking.end_location = booking.start_location
    
    booking.status = False
    booking.removeFromCalendar(service)
    bdb.session.commit()
    car = Car.query.filter_by(carnumber=booking.carnumber).first()
    car.isAvailable = True
    car.maintenance = 1
    car.location = booking.end_location
    cdb.session.commit()
    
    bdb.session.commit()
    cars = Car.query.all()
    form = FilterForm()
    return render_template('main.html', form = form, cars = cars, user = request.args['user'])
        

@app.route("/prev_bookings", methods=['GET', 'POST'])
def prev_bookings():
    bookings = Booking.query.filter(Booking.user==request.args['user']).filter(Booking.status==False)
    return render_template('oldbookings.html', bookings=bookings, user = request.args['user'])

@app.route("/curr_bookings", methods=['GET', 'POST'])
def curr_bookings():
    bookings = Booking.query.filter(Booking.user==request.args['user'],Booking.status==True)
    
    return render_template('currbookings.html', bookings=bookings, user = request.args['user'])


@app.route("/admin_main_page", methods=['GET', 'POST'])
def admin_main_page():
    form = FilterForm()
    cars = Car.query.filter(Car.isArhieved==False)
    if request.method=='POST':
        
        if (form.search.data==None or form.search.data=='' or form.search.data==[]):
            cars1 = Car.query.filter(Car.isArhieved==False)
        else:
            cars1 = Car.query.filter(or_(Car.carnumber==form.search.data, Car.model==form.search.data))
        
        if (form.available.data=="available cars only"):
            cars2 = Car.query.filter(and_(Car.isAvailable==True, Car.maintenance==False))
        elif (form.available.data=="all cars"):
            cars2 = Car.query.filter(Car.isArhieved==False)
        else:
            cars2 = Car.query.filter(Car.isArhieved==False)

        
        if (form.cost_below.data==None or form.cost_below.data=='' or form.cost_below.data==[]):
            cars3 = Car.query.filter(Car.isArhieved==False)
        else:
            cars3 = Car.query.filter(and_(Car.cost_per_hour<=form.cost_below.data, Car.isArhieved==False))
        
        if (form.body.data==None or form.body.data=='' or form.body.data==[]):
            cars4= Car.query.filter(Car.isArhieved==False)
        else:
            if (form.body.data=="SUV"):
                cars4 = Car.query.filter(and_(Car.body_type=="suv",Car.isArhieved==False))
            elif (form.body.data=="sedan"):
                cars4 = Car.query.filter(and_(Car.body_type=="sedan", Car.isArhieved==False))
            else:
                cars4 = Car.query.filter(and_(Car.body_type=="hatch", Car.isArhieved==False))
         
        print(list(set(cars1) & set(cars2) & set(cars3) & set(cars4)))
        cars = list(set(cars1) & set(cars2) & set(cars3) & set(cars4))
        if (cars is None or cars==None or len(cars)==0):
            flash('No results found, please re-edit filters!', 'danger')
            cars = Car.query.filter(Car.isArhieved==False)
        return render_template('admin_main.html', form = form, cars=cars, user = request.args['user'])
    return render_template('admin_main.html', form = form, cars=cars, user = request.args['user'])

@app.route("/admin_booking_history", methods=['GET', 'POST'])
def admin_booking_history():
    form = SearchForm()
    bookings = Booking.query.all()
    if request.method=='POST':
        bookings = Booking.query.filter(or_(Booking.user==form.search.data,Booking.carnumber==form.search.data))
        return render_template('admin_bookings.html', form=form, bookings=bookings, user = request.args['user'])
    return render_template('admin_bookings.html', form=form, bookings=bookings, user = request.args['user'])

@app.route("/admin_delete_car", methods=['GET', 'POST'])
def admin_delete_car():
    car = Car.query.filter(Car.carnumber==request.args['carnumber']).first()
    car.isArhieved = True
    car.isAvailable = False
    cdb.session.commit()
    return redirect(url_for('admin_main_page',  user = request.args['user']))

@app.route("/admin_report", methods=['GET', 'POST'])
def admin_report():
    issue = Issue(reportID=request.args['carnumber']+'-'+str(date.today()), reportedOn=date.today(), reportedBy=request.args['user'], solvedBy=None, isOpen=True, closedOn=None, carnumber=request.args['carnumber'])
    idb.session.add(issue)
    idb.session.commit()
    car = Car.query.filter(Car.carnumber==request.args['carnumber']).first()
    car.maintenance = 2;
    cdb.session.commit();
    #os.system('/home/pi/Desktop/Assignmnet02/pushbullet.sh"A car has been reported. Please login to check."')
    push = pb.push_note("New Job added!", "A car has been reported. Please login to check.")
    my_channel = pb.channels[0]
    push = my_channel.push_note("New Job added!", "A car has been reported. Please login to check.")
    flash('Issue reported to engineers', 'success')
    return redirect(url_for('admin_main_page', user = request.args['user']))

@app.route("/admin_add_car", methods=['GET', 'POST'])
def admin_add_car():
    form = AdminAddCarForm()
    if form.validate_on_submit()==True:
        car = Car(carnumber = form.carnumber.data, model = form.model.data, color = form.color.data, feature = form.feature.data, body_type = form.body_type.data, seats = 0, location = form.location.data, cost_per_hour = form.cost_per_hour.data, photo = form.photo.data, isAvailable=True, isArhieved=False, maintenance=0)
        if(form.body_type.data=='SUV'):
            car.seats = 7
        else:
            car.seats = 5
        cdb.session.add(car)
        cdb.session.commit()
        flash('car added!', 'success')
        return redirect(url_for('admin_main_page', form = form, user = request.args['user']))
    return render_template('admin_add_car.html', title='add product', form=form, user = request.args['user'])

@app.route("/admin_add_staff", methods=['GET', 'POST'])
def admin_add_staff():
    form = AdminRegistrationForm()
    if form.validate_on_submit()==True:
        flash('Account created!', 'success')
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if (form.staffType.data=='Admin'):
            admin = Admin(EmployeeID=form.EmployeeID.data, password = hashed_password, salary = form.salary.data)
            db.session.add(admin);
            db.session.commit();
        elif (form.staffType.data=='Engineer'):
            engineer = Engineer(EmployeeID=form.EmployeeID.data, password = hashed_password, salary = form.salary.data)
            db.session.add(engineer);
            db.session.commit();
            pb.new_contact(form.EmployeeID.data, form.email.data)
        else:
            manager = Manager(EmployeeID=form.EmployeeID.data, password = hashed_password, salary = form.salary.data)
            db.session.add(manager);
            db.session.commit();
        return redirect(url_for('admin_main_page', form = form, user = request.args['user']))
    return render_template('admin_add_staff.html', title='Register', form=form, user = request.args['user'])

@app.route("/admin_view_users", methods=['GET', 'POST'])
def admin_view_users():
    form = SearchForm()
    users = User.query.all()
    if request.method=='POST':
        
        if (form.search.data):
            users = User.query.filter(or_(User.username==form.search.data, User.email==form.search.data))
        return render_template('admin_view_users.html', form = form, users=users, user = request.args['user'])
    return render_template('admin_view_users.html', form = form, users=users, user = request.args['user'])

@app.route("/admin_update_user", methods=['GET', 'POST'])
def admin_update_user():
    form = AdminUpdateForm()
    user = User.query.filter(User.username==request.args['username']).first()
    form.oldEmail.data = user.email
    form.username.data = user.username
    if request.method=='POST':
        if (form.email.data):
            user.email = form.email.data
        db.session.commit()
        flash('Account updated!', 'success')
        return redirect(url_for('admin_view_users', form = form, user = request.args['user']))
    return render_template('admin_update_user.html', form = form, username=request.args['username'] , user = request.args['user'])


@app.route("/engineer_main_page", methods=['GET', 'POST'])
def engineer_main_page():
    cars = Car.query.filter(and_(Car.isArhieved==False, Car.maintenance == 2))
    return render_template('engineer_main.html', cars=cars, user = request.args['user'])

@app.route("/engineer_view_completed_jobs", methods=['GET', 'POST'])
def engineer_view_completed_jobs():
    issues = Issue.query.filter(Issue.solvedBy==request.args['user'])
    return render_template('engineer_view_completed_jobs.html', issues = issues, user = request.args['user'])

@app.route("/engineer_show_location", methods=['GET', 'POST'])
def engineer_show_location():
    #endpoint = 'https://www.googleapis.com/geolocation/v1/geolocate?'
    #api_key = 'AIzaSyD3rq-QIZhzsuTZ65qAgxXJIzmmNyuH1so'
    client = googlemaps.Client(key='AIzaSyCmT9gDmMEKmFBl_x3Rb01hvKpdhD1h-lA')
    results = client.geolocate()
    new_results = client.reverse_geocode((results['location']['lat'],results['location']['lng']))
    print(new_results[0]['place_id'])
    location =new_results[0]['place_id']
    re = client.place(location)
    return render_template('car_location.html', pos=results , user = request.args['user'])

    #[0]['formatted_address']#ChIJC3GC8g481moRyNQkqYNxrU8


@app.route("/manager_main_page", methods=['GET', 'POST'])
def manager_main_page():
    cars = Car.query.all()
    countOfBookings = []
    for car in cars:
        bookings = Booking.query.filter(Booking.carnumber==car.carnumber)
        c=0
        for booking in bookings:
            c+=1
        countOfBookings.append(c)
    countOfIssues = []
    for car in cars:
        issues = Issue.query.filter(Issue.carnumber==car.carnumber)
        c=0
        for issue in issues:
            c+=1
        countOfIssues.append(c)
    users = User.query.all()
    countOfBookingsPerUser = []
    for user in users:
        bookings = Booking.query.filter(Booking.user == user.username)
        c=0
        for booking in bookings:
            c+=1
        countOfBookingsPerUser.append(c)
    return render_template('manager_main_page.html', countOfBookingsPerUser =countOfBookingsPerUser, users=users, cars = cars,countOfIssues =countOfIssues , countOfBookings =countOfBookings, user = request.args['user'])


if (__name__) == '__main__':
    app.run(debug=True)


