import os
from flask_dance.contrib.google import make_google_blueprint, google
from web_app import db
from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import current_user, login_required
from web_app.models import User, File, Settings
from web_app.general.forms import EditProfileForm, UploadDocForm, SettingsForm
from datetime import datetime, timedelta
from web_app.utilities import time_diff, upload_pfp_to_s3, upload_doc_to_s3, generate_url
from web_app.general import bp
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
import urllib.parse

IMAGE_UPLOAD_FOLDER = "web_app/images"
BUCKET = "rezume-files"

@bp.route('/')
def home():
    if current_user.is_authenticated:
        users = User.query.all()
        pfp_links = {user.username: generate_url(BUCKET, f"images/{user.pfp_id}.jpg") for user in users}
        pfp_url = pfp_links[current_user.username]
        return render_template('general/user_home.html', users=users, pfp_links=pfp_links, pfp_url=pfp_url)
    else:
        return render_template('general/home.html')


@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    form = EditProfileForm(request.form)
    user = User.query.filter_by(username=username).first_or_404()
    last_seen = time_diff(user.last_online)
    pfp_file = f"images/{user.pfp_id}.jpg"
    pfp_url = generate_url(BUCKET, pfp_file)

    if form.validate_on_submit():
        try:
            img = request.files['profile_pic']
            content_type = request.mimetype
            upload_pfp_to_s3(img, BUCKET, f"images/{user.pfp_id}.jpg", content_type)
        except:
            pass

        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.username = form.username.data
        user.headline = form.headline.data
        user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('general.user', username=user.username, pfp_url=pfp_url))
    elif request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.username.data = user.username
        form.headline.data = user.headline
        form.about_me.data = user.about_me

    return render_template('general/user.html', user=user, form=form, last_seen=last_seen, pfp_url=pfp_url)


@bp.route('/user_files/<username>', methods=['GET', 'POST'])
@login_required
def user_files(username):
    if current_user.username != username:
        return redirect(url_for('general.home'))

    form = UploadDocForm(CombinedMultiDict((request.files, request.form)))
    user = User.query.filter_by(username=username).first_or_404()
    pfp_file = f"images/{user.pfp_id}.jpg"
    pfp_url = generate_url(BUCKET, pfp_file)
    files = File.query.filter_by(user_id=user.id)
    file_list = {file.filename: file.last_modified for file in files}

    if form.validate_on_submit():
        try:
            doc = form.document.data
            filename = doc.filename
            content_type = request.mimetype
            upload_doc_to_s3(doc, BUCKET, f"documents/{user.pfp_id}{filename}", content_type)
            check = File.query.filter_by(filename=filename, user_id=user.id).first()
            if check is not None:
                check.last_modified = datetime.utcnow()
            else:
                file = File(filename=filename, user_id=user.id)
                db.session.add(file)
            db.session.commit()
        except:
            pass
        return redirect(url_for('general.user_files', username=user.username, pfp_url=pfp_url))

    return render_template('general/user_files.html', user=user, pfp_url=pfp_url, form=form, file_list=file_list)


@bp.route('/document/<user_id>/<filename>', methods=['GET', 'POST'])
@login_required
def document(user_id, filename):
    user = User.query.filter_by(id=user_id).first_or_404()
    pfp_file = f"images/{user.pfp_id}.jpg"
    pfp_url = generate_url(BUCKET, pfp_file)
    return render_template('general/document.html',
                           file_url=urllib.parse.quote(generate_url(BUCKET, f"documents/{user.pfp_id}{filename}")), pfp_url=pfp_url)

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm(request.form)
    user = User.query.filter_by(id=current_user.id).first_or_404()
    pfp_file = f"images/{user.pfp_id}.jpg"
    pfp_url = generate_url(BUCKET, pfp_file)

    if form.validate_on_submit():
        for setting in form:
            if setting.name == 'save' or setting.name == 'csrf_token':
                continue
            query = Settings.query.filter_by(user_id=user.id, key=setting.name).first()
            if query is None:
                db.session.add(Settings(key=setting.name, value=setting.data, user_id=user.id))
            else:
                query.value = setting.data

        db.session.commit()
        return redirect(url_for('general.user', username=user.username, pfp_url=pfp_url))

    elif request.method == 'GET':
        seller_account = Settings.query.filter_by(user_id=current_user.id, key='seller_account').first()
        show_profile_views = Settings.query.filter_by(user_id=current_user.id, key='show_profile_views').first()
        show_last_seen = Settings.query.filter_by(user_id=current_user.id, key='show_last_seen').first()
        data_map = {'0': False, '1': True}

        form.seller_account.data = data_map[seller_account.value] if seller_account is not None else False
        form.show_profile_views.data = data_map[show_profile_views.value] if show_profile_views is not None else True
        form.show_last_seen.data = data_map[show_last_seen.value] if show_last_seen is not None else True

    return render_template('general/settings.html', pfp_url=pfp_url, form=form)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        user = User.query.filter_by(username=current_user.username).first_or_404()
        user.last_online = datetime.utcnow()
        db.session.commit()

