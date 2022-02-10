from web_app import db
from web_app.models import Settings, FileAssociation, User, File

default_settings = {
    "seller_account": False,
    "show_profile_views": True,
    "show_last_seen": True,
}


def init_settings(user_id):
    for setting in default_settings:
        db.session.add(
            Settings(key=setting, value=default_settings[setting], user_id=user_id)
        )

    db.session.commit()


def get_user_files(user_id, filter):
    if filter == "my-files":
        file_assoc = (
            db.session.query(File, FileAssociation)
            .add_columns(
                File.id,
                File.filename,
                File.last_modified,
                FileAssociation.user_status,
                File.user_id,
            )
            .filter_by(file_status="active")
            .outerjoin(FileAssociation, File.id == FileAssociation.file_id)
            .filter_by(user_id=user_id, user_status="owner")
        )
    elif filter == "shared":
        file_assoc = (
            db.session.query(File, FileAssociation)
            .add_columns(
                File.id,
                File.filename,
                File.last_modified,
                FileAssociation.user_status,
                File.user_id,
                FileAssociation.request_status,
            )
            .filter_by(file_status="active")
            .outerjoin(FileAssociation, File.id == FileAssociation.file_id)
            .filter_by(user_id=user_id, user_status="shared", request_status="accepted")
        )
    elif filter == "archive":
        file_assoc = (
            db.session.query(File, FileAssociation)
            .add_columns(
                File.id,
                File.filename,
                File.last_modified,
                FileAssociation.user_status,
                File.user_id,
            )
            .filter_by(file_status="archived")
            .outerjoin(FileAssociation, File.id == FileAssociation.file_id)
            .filter_by(user_id=user_id, user_status="owner")
        )

    file_list = [
        {
            "filename": file.filename,
            "last_modified": file.last_modified,
            "owner": "me"
            if file.user_status == "owner"
            else User.query.filter_by(id=file.user_id).first().username,
            "file_id": file.id,
            "owner_id": User.query.filter_by(id=file.user_id).first().id,
        }
        for file in file_assoc
    ]
    return file_list


def get_requests(user_id, type):
    if type == "sent":
        file_assoc = (
            db.session.query(File, FileAssociation)
            .add_columns(
                File.id,
                File.filename,
                FileAssociation.user_status,
                FileAssociation.user_id,
                FileAssociation.request_status,
            )
            .outerjoin(FileAssociation, File.id == FileAssociation.file_id)
            .filter(File.user_id == user_id, FileAssociation.user_status == "shared")
        )
        request_list = [
            {
                "filename": file.filename,
                "reviewer": User.query.filter_by(id=file.user_id).first().username,
                "status": file.request_status,
                "owner_id": File.query.filter_by(id=file.id).first().user_id,
                "file_id": file.id,
            }
            for file in file_assoc
        ]

    elif type == "received":
        file_assoc = (
            db.session.query(File, FileAssociation)
            .add_columns(
                File.id,
                File.filename,
                FileAssociation.user_status,
                File.user_id,
                FileAssociation.request_status,
            )
            .outerjoin(FileAssociation, File.id == FileAssociation.file_id)
            .filter(
                FileAssociation.user_id == user_id,
                FileAssociation.user_status == "shared",
            )
        )
        request_list = [
            {
                "filename": file.filename,
                "reviewer": User.query.filter_by(id=file.user_id).first().username,
                "status": file.request_status,
                "file_id": file.id,
            }
            for file in file_assoc
        ]

    return request_list
