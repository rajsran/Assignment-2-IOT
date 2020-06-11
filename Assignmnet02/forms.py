from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, PasswordField, FileField, SubmitField, DateField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_api import User
from datetime import date

class FilterForm(FlaskForm):
    search = StringField('search')
    available = RadioField('available', choices=[('available cars only','available cars only'),('all cars','all cars')])
    cost_below = DecimalField('cost_below')
    body = RadioField('body', choices=[('SUV','SUV'),('sedan','sedan'),('hatch back','hatch back')])
    submit = SubmitField('Apply Filters')
    
class SearchForm(FlaskForm):
    search = StringField('search')
    submit = SubmitField('Search')
    
    
class RegistrationForm(FlaskForm):
    username = StringField('username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    dp = FileField('dp')
    submit = SubmitField('sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username already exists.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('An account with this email already exists.')



class LoginForm(FlaskForm):
    email = StringField('email',
                        validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('login')
    
    
class BookingForm(FlaskForm):
    booking_id = StringField('booking_id')
    carnumber = StringField('carnumber',validators=[DataRequired()])
    user = StringField('user', validators=[DataRequired()])
    start_date = DateField('start_date', validators=[DataRequired()])
    end_date = DateField('end_date', validators=[DataRequired()])
    start_location = StringField('start_location')
    end_location = StringField('end_location')
    number_of_days = IntegerField('number_of_days', validators = [DataRequired()])
    cost = DecimalField('cost', validators=[DataRequired()])
    submit = SubmitField('book')
    
    
    def setnod(self, sd,ed):
        '''date_format= "%m/%d/%y"
            date1 = datetime.strptime(self.start_date.data, date_format)
            date2 = datetime.strptime(self.end_date.data, date_format)'''
        number_of_days = ed.data-sd.data
        return number_of_days
    
    def setcost(self,number_of_days,price):
        cost = number_of_days.data * price
        return cost
    
    def validate_start_date(self, start_date):
        if ((start_date.data<date.today())):
            raise ValidationError('Booking can not be in the past.')
        
    def validate_end_date(self, end_date):
        if ((end_date.data<self.start_date.data)):
            raise ValidationError('Booking should end after start date.')
        
class updateForm(FlaskForm):
    newprice = DecimalField('newprice')
    newdesc = StringField('newdesc')
    submit = SubmitField('update')
    
    
class AdminAddCarForm(FlaskForm):
    carnumber = StringField('carnumber',validators=[DataRequired()])
    model = StringField('model',validators=[DataRequired()])
    color = StringField('color',validators=[DataRequired()])
    feature = StringField('features',validators=[DataRequired()])
    body_type = StringField('body_type',validators=[DataRequired()])
    seats = IntegerField('seats')
    location = StringField('location',validators=[DataRequired()])
    cost_per_hour = DecimalField('cost_per_hour', validators=[DataRequired()])
    photo = StringField('photo',validators=[DataRequired()])
    submit = SubmitField('add')
    
class AdminRegistrationForm(FlaskForm):
    staffType = StringField('staffType',
                           validators=[DataRequired()])
    EmployeeID = StringField('EmployeeID',
                        validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    salary = DecimalField('salary', validators=[DataRequired()])
    submit = SubmitField('sign Up')

    def validate_username(self, username):
        return True

    def validate_email(self, email):
        return True
    
class AdminUpdateForm(FlaskForm):
    username = StringField('New username')
    oldEmail = StringField('Old email')
    email = StringField('New email')
    submit = SubmitField('Update')
    