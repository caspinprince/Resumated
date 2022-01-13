from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from flask import render_template, redirect, url_for
from flask_login import current_user

from web_app.models import User

class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    headline = StringField('Headline', validators=[Length(min=0, max=250)])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=1000)])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first() and username.data != current_user.username:
            raise ValidationError('Username is already taken!')