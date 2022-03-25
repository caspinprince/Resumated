from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user

from web_app import db
from web_app.social import bp
from web_app.models import User


@bp.route("/connect/<int:user_id>", methods=["POST"])
@login_required
def connect(user_id):
    user = User.query.filter_by(id=user_id).first()
    current_user.request_connect(user)

    return redirect(url_for("general.home"))