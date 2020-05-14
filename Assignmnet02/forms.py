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
                        validators=[DataRequired(), Email()])
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