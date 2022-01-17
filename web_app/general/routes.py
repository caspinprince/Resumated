import os
from flask_dance.contrib.google import make_google_blueprint, google
from web_app import db
from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import current_user, login_required
from web_app.models import User
from web_app.general.forms import EditProfileForm
from datetime import datetime, timedelta
from utilities import time_diff, upload_to_s3
from web_app.general import bp
from werkzeug.utils import secure_filename


IMAGE_UPLOAD_FOLDER = "web_app/images"
BUCKET = "rezume-files"

@bp.route('/')
def home():
    if current_user.is_authenticated:
        users = User.query.all()
        return render_template('general/user_home.html', users=users)
    else:
        return render_template('general/home.html')


@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    form = EditProfileForm(request.form)
    user = User.query.filter_by(username=username).first_or_404()
    last_seen = time_diff(user.last_online)

    if form.validate_on_submit():
        img = request.files['profile_pic']
        content_type = request.mimetype
        upload_to_s3(img, BUCKET, f"images/{secure_filename(img.filename)}", content_type)

        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.username = form.username.data
        user.headline = form.headline.data
        user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('general.user', username=user.username))
    elif request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.username.data = user.username
        form.headline.data = user.headline
        form.about_me.data = user.about_me

    return render_template('general/user.html', user=user, form=form, last_seen=last_seen)

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        user = User.query.filter_by(username=current_user.username).first_or_404()
        user.last_online = datetime.utcnow()
        db.session.commit()

