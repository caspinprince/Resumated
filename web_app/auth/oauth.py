import os

from flask import redirect, url_for
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import login_user
from sqlalchemy.orm.exc import NoResultFound

from web_app import db
from web_app.models import User
from web_app.utilities import init_settings

blueprint = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"),
    offline=True,
    scope=["profile", "email"],
)


@oauth_authorized.connect_via(blueprint)
def google_logged_in(blueprint, token):
    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        print(resp.json())
        google_id = resp.json()["id"]
        email = resp.json()["email"]
        first_name = resp.json()["given_name"]
        last_name = resp.json()["family_name"]
        username = email.split("@")[0]

        query = User.query.filter_by(email=email)
        try:
            user = query.one()
        except NoResultFound:
            user = User(
                google_id=google_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                username=username,
            )
            db.session.add(user)
            db.session.commit()
            init_settings(user.id)
        else:
            User.query.filter_by(email=email).first().google_id = google_id
            db.session.commit()
        login_user(user)

        return redirect(url_for("general.home"))
