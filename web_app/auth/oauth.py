import os
from flask_dance.contrib.google import make_google_blueprint, google
from sqlalchemy.orm.exc import NoResultFound
from flask_login import current_user, login_user
from flask_dance.consumer import oauth_authorized
from web_app import app, db
from web_app.models import User
from flask import redirect, url_for

blueprint = make_google_blueprint(client_id=os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
                                  client_secret=os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"),
                                  offline=True, scope=['profile', 'email'])

@oauth_authorized.connect_via(blueprint)
def google_logged_in(blueprint, token):
    resp = google.get('/oauth2/v2/userinfo')
    if resp.ok:
        google_id = resp.json()['id']
        email = resp.json()['email']
        first_name = resp.json()['given_name']
        last_name = resp.json()['family_name']
        username = email.split("@")[0]

        query = User.query.filter_by(email=email)
        try:
            user = query.one()
        except NoResultFound:
            user = User(google_id=google_id,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        username=username)
            db.session.add(user)
            db.session.commit()
        else:
            User.query.filter_by(email=email).first().google_id = google_id
            db.session.commit()
        login_user(user)

        return redirect(url_for('home'))
