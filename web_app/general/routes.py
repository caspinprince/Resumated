import urllib.parse
from datetime import datetime

from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required
from werkzeug.datastructures import CombinedMultiDict
from web_app import db, cache
from web_app.general import bp
from sqlalchemy import func
from web_app.general.forms import (
    EditProfileForm,
    UploadDocForm,
    SettingsForm,
    RequestReviewForm,
    ReviewForm,
    SearchForm,
)
from web_app.models import User, File, Settings, FileAssociation, Feedback
from web_app.utilities import (
    time_diff,
    upload_pfp_to_s3,
    upload_doc_to_s3,
    generate_url,
    get_user_files,
    delete_object_s3,
    get_requests,
)

IMAGE_UPLOAD_FOLDER = "web_app/images"
BUCKET = "rezume-files"


@bp.route("/")
@bp.route("/explore", methods=["POST", "GET"], defaults={"page": 1})
@bp.route("/explore/<int:page>", methods=["POST", "GET"])
def home(page=None):
    if current_user.is_authenticated:
        search_form = SearchForm(request.form)
        users = (
            db.session.query(
                User.id,
                User.username,
                User.pfp_id,
                User.first_name,
                User.last_name,
                User.about_me,
                User.headline,
                Settings.value,
                Settings.key,
            )
            .join(User.settings)
            .filter(Settings.key == "seller_account")
        )

        if search_form.validate_on_submit():
            search = search_form.search.data
            users = users.filter(
                (func.lower(User.first_name).like(func.lower(f"%{search}%")))
                | func.lower(User.last_name).like(func.lower(f"%{search}%"))
            )
        pfp_links = {}
        users = users.paginate(page, 12, True)
        for user in users.items:
            if cache.get(str(user.id)) is not None:
                print('have in cache')
                pfp_links[user.id] = cache.get(str(user.id))
            else:
                print('not in cache')
                pfp_links[user.id] = generate_url(BUCKET, f"images/{user.pfp_id}.jpg")
                cache.set(str(user.id), pfp_links[user.id])

        return render_template(
            "general/user_home.html",
            users=users,
            pfp_links=pfp_links,
            search_form=search_form,
        )
    else:
        return render_template("general/home.html")


@bp.route("/user/<username>", methods=["GET", "POST"])
@login_required
def user(username):
    profile_form = EditProfileForm(CombinedMultiDict((request.files, request.form)))

    review_form = RequestReviewForm(request.form)
    review_form.document.choices = [
        (x["file_id"], x["filename"])
        for x in get_user_files(current_user.id, "my-files")
    ]

    user = User.query.filter_by(username=username).first_or_404()
    last_seen = time_diff(user.last_online)

    user_pfp_file = f"images/{user.pfp_id}.jpg"
    user_pfp_url = generate_url(BUCKET, user_pfp_file)
    seller_account = Settings.query.filter_by(
        user_id=user.id, key="seller_account"
    ).first()

    show_join_date = Settings.query.filter_by(
        user_id=user.id, key="show_join_date"
    ).first()
    show_last_seen = Settings.query.filter_by(
        user_id=user.id, key="show_last_seen"
    ).first()

    if current_user.username == username:
        if profile_form.validate_on_submit():
            try:
                img = request.files["profile_pic"]
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
            return redirect(url_for("general.user", username=user.username))
        elif request.method == "GET":
            profile_form.first_name.data = user.first_name
            profile_form.last_name.data = user.last_name
            profile_form.username.data = user.username
            profile_form.headline.data = user.headline
            profile_form.about_me.data = user.about_me
    else:
        if review_form.validate_on_submit():
            file_id = review_form.document.data
            requests = review_form.requests.data
            assoc = FileAssociation(
                user_status="shared",
                user_id=user.id,
                file_id=file_id,
                requests=requests,
                request_status="pending",
            )
            assoc.file = File.query.filter_by(id=file_id).first()
            user.files.append(assoc)
            db.session.add(user)
            db.session.commit()

    return render_template(
        "general/user.html",
        user=user,
        profile_form=profile_form,
        review_form=review_form,
        last_seen=last_seen,
        show_join_date=show_join_date,
        show_last_seen=show_last_seen,
        user_pfp_url=user_pfp_url,
        seller_account=seller_account,
    )


@bp.route("/user_files/<username>/<filter>", methods=["GET", "POST"])
@login_required
def user_files(username, filter):
    if current_user.username != username:
        return redirect(url_for("general.home"))

    form = UploadDocForm(CombinedMultiDict((request.files, request.form)))
    user = User.query.filter_by(username=username).first_or_404()
    file_list = get_user_files(user.id, filter)

    if form.validate_on_submit():
        try:
            doc = form.document.data
            filename = doc.filename
            content_type = request.mimetype
            upload_doc_to_s3(
                doc, BUCKET, f"documents/{user.pfp_id}{filename}", content_type
            )
            check = File.query.filter_by(filename=filename, user_id=user.id).first()
            if check is not None:
                check.last_modified = datetime.utcnow()
            else:
                assoc = FileAssociation(user_status="owner")
                assoc.file = File(
                    filename=filename, user_id=user.id, file_status="active"
                )
                current_user.files.append(assoc)
                db.session.add(current_user)
            db.session.commit()
        except:
            pass
        return redirect(
            url_for(
                "general.user_files",
                username=user.username,
                filter="my-files",
            )
        )

    return render_template(
        "general/user_files.html",
        user=user,
        form=form,
        file_list=file_list,
        filter=filter,
    )


@bp.route("/document/<user_id>/<filename>", methods=["GET", "POST"])
@login_required
def document(user_id, filename):
    form = ReviewForm(request.form)
    user = User.query.filter_by(id=user_id).first()

    owner = int(user_id) == current_user.id
    file = File.query.filter_by(filename=filename, user_id=user_id).first()
    requests = (
        FileAssociation.query.filter_by(file_id=file.id, user_id=current_user.id)
        .first()
        .requests
    )

    if form.validate_on_submit():
        db.session.add(
            Feedback(
                file_id=file.id, feedback=form.review.data, user_id=current_user.id
            )
        )
        FileAssociation.query.filter_by(
            file_id=file.id, user_id=current_user.id
        ).update({FileAssociation.request_status: "complete"})

        db.session.commit()
        return redirect(
            url_for(
                "general.user_files",
                username=current_user.username,
                filter="my-files",
            )
        )

    feedback = Feedback.query.filter_by(file_id=file.id)
    feedback_data = []
    for comment in feedback:
        data = {}
        person = User.query.filter_by(id=comment.user_id).first()
        data["name"] = f"{person.first_name} {person.last_name} ({person.username})"
        data["feedback"] = comment.feedback
        feedback_data.append(data)
    return render_template(
        "general/document.html",
        file_url=urllib.parse.quote(
            generate_url(BUCKET, f"documents/{user.pfp_id}{filename}")
        ),
        form=form,
        owner=owner,
        feedback_data=feedback_data,
        requests=requests,
    )


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = SettingsForm(request.form)
    user = User.query.filter_by(id=current_user.id).first()

    if form.validate_on_submit():
        for setting in form:
            if setting.name == "save" or setting.name == "csrf_token":
                continue
            query = Settings.query.filter_by(user_id=user.id, key=setting.name).first()
            if query is None:
                db.session.add(
                    Settings(key=setting.name, value=setting.data, user_id=user.id)
                )
            else:
                query.value = setting.data

        db.session.commit()
        return redirect(url_for("general.user", username=user.username))

    elif request.method == "GET":
        seller_account = Settings.query.filter_by(
            user_id=current_user.id, key="seller_account"
        ).first()
        show_join_date = Settings.query.filter_by(
            user_id=current_user.id, key="show_join_date"
        ).first()
        show_last_seen = Settings.query.filter_by(
            user_id=current_user.id, key="show_last_seen"
        ).first()
        data_map = {"0": False, "1": True}

        form.seller_account.data = (
            data_map[seller_account.value] if seller_account is not None else False
        )
        form.show_join_date.data = (
            data_map[show_join_date.value]
            if show_join_date is not None
            else True
        )
        form.show_last_seen.data = (
            data_map[show_last_seen.value] if show_last_seen is not None else True
        )

    return render_template("general/settings.html", form=form)


@bp.route("/requests/<type>", methods=["GET", "POST"])
@login_required
def requests(type):
    request_list = get_requests(current_user.id, type)
    return render_template(
        "general/requests.html", type=type, request_list=request_list
    )


@bp.route("/delete_file/<int:file_id>/<delete_or_archive>", methods=["POST"])
@login_required
def delete_file(file_id, delete_or_archive):
    if current_user.id == File.query.filter_by(id=file_id).first().user_id:
        if delete_or_archive == "del":
            file = File.query.filter_by(id=file_id).first()
            db.session.delete(file)
            delete_object_s3(BUCKET, f"documents/{current_user.pfp_id}{file.filename}")
        else:
            File.query.filter_by(id=file_id).update({File.file_status: "archived"})
        db.session.commit()
    return redirect(
        url_for(
            "general.user_files",
            username=current_user.username,
            filter="my-files",
        )
    )


@bp.route("/accept/<int:file_id>/<accepted_or_declined>", methods=["POST"])
@login_required
def accept(file_id, accepted_or_declined):
    FileAssociation.query.filter_by(file_id=file_id, user_id=current_user.id).update(
        {FileAssociation.request_status: accepted_or_declined}
    )
    db.session.commit()

    return redirect(url_for("general.requests", type="received"))


@bp.route("/privacy", methods=["GET"])
def privacy():
    return render_template("general/privacy.html")


@bp.route("/delete_user", methods=["POST"])
@login_required
def delete_user():
    delete_object_s3(BUCKET, f"images/{current_user.pfp_id}.jpg")

    files = File.query.filter_by(user_id=current_user.id)
    for file in files:
        delete_object_s3(BUCKET, f"documents/{current_user.pfp_id}{file.filename}")

    User.query.filter_by(id=current_user.id).delete()
    db.session.commit()
    return redirect(url_for("general.home"))


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        user = User.query.filter_by(username=current_user.username).first_or_404()
        user.last_online = datetime.utcnow()
        db.session.commit()


@bp.context_processor
def current_user_info():
    if current_user.is_authenticated:
        pfp_file = f"images/{current_user.pfp_id}.jpg"
        pfp_url = generate_url(BUCKET, pfp_file)
        pending_reviews = FileAssociation.query.filter_by(user_id=current_user.id, user_status='shared', request_status='pending').count()
        return {
            "account_type": Settings.query.filter_by(
                user_id=current_user.id, key="seller_account"
            )
            .first()
            .value,
            "pfp_url": pfp_url,
            "pending_reviews": pending_reviews
        }
    else:
        return {}


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template("general/404.html"), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("general/500.html"), 500
