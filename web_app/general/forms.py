from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileSize
from wtforms import (
    StringField,
    SubmitField,
    BooleanField,
    TextAreaField,
    FileField,
    SelectField,
)
from wtforms.validators import DataRequired, Length, ValidationError

from web_app.models import User


class EditProfileForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    headline = StringField("Headline", validators=[Length(min=0, max=250)])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=1000)])
    profile_pic = FileField(
        label="Select a profile picture! (jpg or png)",
        validators=[FileAllowed(["jpg", "png"]), FileSize(max_size=1000000)],
    )
    submit = SubmitField("Submit")

    def validate_username(self, username):
        if (
            User.query.filter_by(username=username.data).first()
            and username.data != current_user.username
        ):
            raise ValidationError("Username is already taken!")


class UploadDocForm(FlaskForm):
    filename = StringField("File Name", validators=[DataRequired()])
    document = FileField(
        label="Upload a document! (PDF only)",
        validators=[FileAllowed(["pdf"]), FileSize(max_size=2000000)],
    )
    submit = SubmitField("Submit")


class SettingsForm(FlaskForm):
    seller_account = BooleanField(
        "Activate seller account functionalities",
        false_values=(False, "false", "False", "0", 0),
    )
    show_profile_views = BooleanField(
        "Show view count on profile page",
        false_values=(False, "false", "False", "0", 0),
    )
    show_last_seen = BooleanField(
        "Show activity status on profile page",
        false_values=(False, "false", "False", "0", 0),
    )
    save = SubmitField("Save")


class RequestReviewForm(FlaskForm):
    document = SelectField("Select a Document")
    requests = TextAreaField(
        "Special Requests", validators=[DataRequired(), Length(min=0, max=2000)]
    )
    submit = SubmitField("Submit")


class ReviewForm(FlaskForm):
    review = TextAreaField(
        "Comments", validators=[DataRequired(), Length(min=0, max=10000)]
    )
    submit = SubmitField("Submit")


class SearchForm(FlaskForm):
    search = StringField(validators=[DataRequired()])
    submit = SubmitField("Search")
