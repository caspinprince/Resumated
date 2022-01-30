import os
from flask_dance.contrib.google import make_google_blueprint, google
from web_app import db
from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import current_user, login_required
from web_app.models import User, File, Settings, FileAssociation, Feedback
from web_app.general.forms import EditProfileForm, UploadDocForm, SettingsForm, RequestReviewForm, ReviewForm
from datetime import datetime, timedelta
from web_app.utilities import time_diff, upload_pfp_to_s3, upload_doc_to_s3, generate_url, get_user_files
from web_app.general import bp
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
import urllib.parse

IMAGE_UPLOAD_FOLDER = "web_app/images"
BUCKET = "rezume-files"


@bp.route('/')
def home():
    if current_user.is_authenticated:
        users = db.session.query(User.id, User.username, User.pfp_id, User.first_name, User.last_name, User.about_me,
                                 User.headline, Settings.value, Settings.key).join(User.settings) \
            .filter(Settings.key == 'seller_account')
        pfp_links = {user.username: generate_url(BUCKET, f"images/{user.pfp_id}.jpg") for user in users}
        pfp_url = pfp_links[current_user.username]
        return render_template('general/user_home.html', users=users, pfp_links=pfp_links, pfp_url=pfp_url)
    else:
        return render_template('general/home.html')


@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    profile_form = EditProfileForm(request.form)

    review_form = RequestReviewForm(request.form)
    review_form.document.choices = [(x['file_id'], x['filename']) for x in get_user_files(current_user.id, "my-files")]

    user = User.query.filter_by(username=username).first_or_404()
    last_seen = time_diff(user.last_online)
    pfp_file = f"images/{current_user.pfp_id}.jpg"
    pfp_url = generate_url(BUCKET, pfp_file)

    user_pfp_file = f"images/{user.pfp_id}.jpg"
    user_pfp_url = generate_url(BUCKET, user_pfp_file)

    seller_account = Settings.query.filter_by(user_id=user.id, key='seller_account').first()
    show_profile_views = Settings.query.filter_by(user_id=user.id, key='show_profile_views').first()
    show_last_seen = Settings.query.filter_by(user_id=user.id, key='show_last_seen').first()

    if current_user.username == username:
        if profile_form.validate_on_submit():
            try:
                img = request.files['profile_pic']
                content_type = request.mimetype
                upload_pfp_to_s3(img, BUCKET, f"images/{user.pfp_id}.jpg", content_type)
            except:
                pass

            user.first_name = profile_form.first_name.data
            user.last_name = profile_form.last_name.data
            user.username = profile_form.username.data
            user.headline = profile_form.headline.data
            user.about_me = profile_form.about_me.data
            db.session.commit()
            return redirect(url_for('general.user', username=user.username))
        elif request.method == 'GET':
            profile_form.first_name.data = user.first_name
            profile_form.last_name.data = user.last_name
            profile_form.username.data = user.username
            profile_form.headline.data = user.headline
            profile_form.about_me.data = user.about_me
    else:
        if review_form.validate_on_submit():
            file_id = review_form.document.data
            assoc = FileAssociation(user_status="shared", file_status="active", user_id=user.id, file_id=file_id)
            assoc.file = File.query.filter_by(id=file_id).first()
            user.files.append(assoc)
            db.session.add(user)
            db.session.commit()

    return render_template('general/user.html', user=user, profile_form=profile_form, review_form=review_form,
                           last_seen=last_seen, pfp_url=pfp_url,
                           show_profile_views=show_profile_views, show_last_seen=show_last_seen,
                           user_pfp_url=user_pfp_url,
                           seller_account=seller_account)


@bp.route('/user_files/<username>/<filter>', methods=['GET', 'POST'])
@login_required
def user_files(username, filter):
    if current_user.username != username:
        return redirect(url_for('general.home'))

    form = UploadDocForm(CombinedMultiDict((request.files, request.form)))
    user = User.query.filter_by(username=username).first_or_404()
    pfp_file = f"images/{user.pfp_id}.jpg"
    pfp_url = generate_url(BUCKET, pfp_file)
    file_list = get_user_files(user.id, filter)

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
                assoc = FileAssociation(user_status="owner", file_status="active")
                assoc.file = File(filename=filename, user_id=user.id)
                current_user.files.append(assoc)
                db.session.add(current_user)
            db.session.commit()
        except Exception as e:
            print(e)
        return redirect(url_for('general.user_files', username=user.username, pfp_url=pfp_url, filter='my-files'))

    return render_template('general/user_files.html', user=user, pfp_url=pfp_url, form=form, file_list=file_list)


@bp.route('/document/<user_id>/<filename>', methods=['GET', 'POST'])
@login_required
def document(user_id, filename):
    form = ReviewForm(request.form)
    user = User.query.filter_by(id=user_id).first()
    pfp_file = f"images/{current_user.pfp_id}.jpg"
    pfp_url = generate_url(BUCKET, pfp_file)

    owner = int(user_id) == current_user.id
    file = File.query.filter_by(filename=filename, user_id=user_id).first()

    if form.validate_on_submit():
        db.session.add(Feedback(file_id=file.id, feedback=form.review.data, user_id=current_user.id))
        FileAssociation.query.filter_by(file_id=file.id, user_id=current_user.id).delete()
        db.session.commit()
        return redirect(url_for('general.user_files', username=current_user.username, pfp_url=pfp_url, filter='my-files'))

    feedback = Feedback.query.filter_by(file_id=file.id)
    feedback_data = []
    for comment in feedback:
        data = {}
        person = User.query.filter_by(id=comment.user_id).first()
        data['name'] = f'{person.first_name} {person.last_name} ({person.username})'
        data['feedback'] = comment.feedback
        feedback_data.append(data)
    return render_template('general/document.html',
                           file_url=urllib.parse.quote(generate_url(BUCKET, f"documents/{user.pfp_id}{filename}")),
                           pfp_url=pfp_url, form=form, owner=owner, feedback_data=feedback_data)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm(request.form)
    user = User.query.filter_by(id=current_user.id).first()
    pfp_file = f"images/{current_user.pfp_id}.jpg"
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


@bp.route('/delete/<int:file_id>/<delete_or_archive>', methods=['POST'])
@login_required
def delete(file_id, delete_or_archive):
    pfp_file = f"images/{current_user.pfp_id}.jpg"
    pfp_url = generate_url(BUCKET, pfp_file)

    if current_user.id == File.query.filter_by(id=file_id).first().user_id:
        if delete_or_archive == 'del':
            file = File.query.filter_by(id=file_id).first()
            db.session.delete(file)
        else:
            FileAssociation.query.filter_by(file_id=file_id).update({FileAssociation.file_status: 'archived'})
        db.session.commit()
    return redirect(url_for('general.user_files', username=current_user.username, pfp_url=pfp_url, filter='my-files'))


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        user = User.query.filter_by(username=current_user.username).first_or_404()
        user.last_online = datetime.utcnow()
        db.session.commit()
