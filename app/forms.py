from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TimeField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
            
class LightConfiguration(FlaskForm):
    starting_time = TimeField('Start Time', validators=[DataRequired()])
    duration = TimeField('End Time', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
    #def update_light():
        
class PlotConfiguration(FlaskForm):
    starting_time = DateTimeField('Start Time', format= '%Y-%m-%d %H:%M:%S',validators=[DataRequired()])
    ending_time = DateTimeField('End Time', format = '%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    submit = SubmitField('Submit')
        
        