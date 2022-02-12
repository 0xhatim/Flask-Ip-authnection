from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField,TextAreaField,IntegerField,validators
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,optional
from falcon_web.model import User # to check if user in db or not
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    register_code = StringField('REGISTER CODE',
                                     validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken')
    def validate_email(self,email):
        email_check = User.query.filter_by(email=email.data).first()
        if email_check:
            raise ValidationError('That email is taken')
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class code_generationr(FlaskForm):
    code_filed = StringField('Enter Code',validators=[DataRequired()])
    submit = SubmitField('Make Code')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    instagram_user = StringField('Instagram username:')
    Telegram_id =  StringField('Telegram [ID]')
    ip_active_proxies = StringField('IP ADDRESS')
    picture = FileField("Update Profile Picture",validators=[FileAllowed(["jpg","png","ico","jpeg"])])
    submit = SubmitField('UPDATE PROFILE')


class RequestsResetForm(FlaskForm):
    email = StringField('Requests Password',validators=[DataRequired(),Email()])
    submit = SubmitField('Send')
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("There is no account with that email")
        

class ResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
