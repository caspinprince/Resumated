from web_app.models import Settings, FileAssociation, User
from web_app import db

default_settings = {'seller_account': False, 'show_profile_views': True, 'show_last_seen': True}

def init_settings(user_id):
    for setting in default_settings:
        db.session.add(Settings(key=setting, value=default_settings[setting], user_id=user_id))

    db.session.commit()

def get_user_files(user_id, filter):
    if filter == 'my-files':
        file_assoc = FileAssociation.query.filter_by(user_id=user_id, user_status='owner', file_status='active')
    elif filter == 'shared':
        file_assoc = FileAssociation.query.filter_by(user_id=user_id, user_status='shared', file_status='active')
    elif filter == 'archive':
        file_assoc = FileAssociation.query.filter_by(user_id=user_id, user_status='owner', file_status='archived')

    file_list = [{'filename': file.file.filename, 'last_modified': file.file.last_modified,
                  'owner': 'me' if file.user_status == 'owner' else User.query.filter_by(id=file.file.user_id).first().username,
                  'file_id': file.file_id, 'owner_id': User.query.filter_by(id=file.file.user_id).first().id} for file in file_assoc]
    return file_list
