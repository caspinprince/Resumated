from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user

from web_app import db
from web_app.social import bp
from web_app.models import User


@bp.route("/request_connect/<int:user_id>", methods=["POST"])
@login_required
def request_connect(user_id):
    user = User.query.filter_by(id=user_id).first()
    current_user.request_connect(user)

    return redirect(url_for("social.connections"))


@bp.route("/accept_connect/<int:user_id>", methods=["POST"])
@login_required
def accept_connect(user_id):
    user = User.query.filter_by(id=user_id).first()
    current_user.accept_connect(user)

    return redirect((url_for("social.connections")))


@bp.route("/connections", methods=["GET"])
@login_required
def connections():
    connections = current_user.all_connections()
    incoming = current_user.pending_connections(incoming=True)
    outgoing = current_user.pending_connections(incoming=False)
    return render_template(
        "social/connections.html",
        connections=connections,
        incoming=incoming,
        outgoing=outgoing,
    )