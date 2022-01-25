from web_app.models import Settings
from web_app import db

default_settings = {'seller_account': False, 'show_profile_views': True, 'show_last_seen': True}

def init_settings(user_id):
    for setting in default_settings:
        db.session.add(Settings(key=setting, value=default_settings[setting], user_id=user_id))

    db.session.commit()