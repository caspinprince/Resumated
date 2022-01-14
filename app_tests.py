import os
import unittest
from flask import current_app
from app import create_app, db
from web_app.models import User
from config import Config


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_MYSQL_DB')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EXPLAIN_TEMPLATE_LOADING = True

class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.config['WTF_CSRF_ENABLED'] = False  # no CSRF during tests
        self.appctx = self.app.app_context()
        self.appctx.push()
        db.create_all()
        self.populate_db()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.appctx.pop()
        self.app = None
        self.appctx = None
        self.client = None

    def populate_db(self):
        user = User(email='example@example.com', first_name='Johnny', last_name='Appleseed',
                    username='example', password='qwertyuiop')
        db.session.add(user)
        db.session.commit()

    def login(self):
        self.client.post('/auth/login', data={
            'email': 'example@example.com',
            'password': 'qwertyuiop',
        })
        assert response.status_code == 200

    def test_app(self):
        assert self.app is not None
        assert current_app == self.app

    def test_home_page_redirect(self):
        response = self.client.get('/user/caspinprince', follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/auth/login'

    def test_registration_form(self):
        response = self.client.get('/auth/signup')
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        assert 'name="email"' in html
        assert 'name="first_name"' in html
        assert 'name="last_name"' in html
        assert 'name="username"' in html
        assert 'name="password"' in html
        assert 'name="submit"' in html


    def test_register_user(self):
        response = self.client.post('/auth/signup', data={
            'email': 'tester@testing.com',
            'first_name': 'Testing',
            'last_name': 'Person',
            'username': 'tester',
            'password': 'qwertyuiop',
            'password_conf': 'qwertyuiop',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/auth/login'

        response = self.client.post('/auth/login', data={
            'email': 'tester@testing.com',
            'password': 'qwertyuiop',
            'remember_me': True
        }, follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/'


    def test_duplicate_email(self):
        self.client.post('/auth/signup', data={
            'email': 'tester@testing.com',
            'first_name': 'Testing',
            'last_name': 'Person',
            'username': 'tester',
            'password': 'qwertyuiop',
            'password_conf': 'qwertyuiop',
        })
        response = self.client.post('/auth/signup', data={
            'email': 'tester@testing.com',
            'first_name': 'Testing',
            'last_name': 'Person',
            'username': 'tester2',
            'password': 'qwertyuiop',
            'password_conf': 'qwertyuiop',
        })
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Email is already registered!' in html

    def test_duplicate_username(self):
        self.client.post('/auth/signup', data={
            'email': '123@gmail.com',
            'first_name': 'Testing',
            'last_name': 'Person',
            'username': 'tester',
            'password': 'qwertyuiop',
            'password_conf': 'qwertyuiop',
        })
        response = self.client.post('/auth/signup', data={
            'email': 'tester@testing.com',
            'first_name': 'Testing',
            'last_name': 'Person',
            'username': 'tester',
            'password': 'qwertyuiop',
            'password_conf': 'qwertyuiop',
        })
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Username is already taken!' in html