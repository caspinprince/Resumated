# run with command: pytest --cov=web_app --cov-report=term-missing --cov-branch app_tests*

import os
import unittest
from flask import current_app, url_for, request
from app import create_app, db
from web_app.models import User
from config import Config
from flask_login import current_user


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
        user_two = User(email='example_two@example.com', first_name='Bill', last_name='Bob',
                        username='example_two', password='qwertyuiop')
        db.session.add(user)
        db.session.add(user_two)
        db.session.commit()

    def login(self, user=1):
        if user == 1:
            return self.client.post('/auth/login', data={
                'email': 'example@example.com',
                'password': 'qwertyuiop',
            }, follow_redirects=True)
        elif user == 2:
            return self.client.post('/auth/login', data={
                'email': 'example_two@example.com',
                'password': 'qwertyuiop',
            }, follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)

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

    def test_duplicate_username_email(self):
        self.client.post('/auth/signup', data={
            'email': '123@gmail.com',
            'first_name': 'Testing',
            'last_name': 'Person',
            'username': 'tester',
            'password': 'qwertyuiop',
            'password_conf': 'qwertyuiop',
        })
        response = self.client.post('/auth/signup', data={
            'email': '123@gmail.com',
            'first_name': 'Testing',
            'last_name': 'Person',
            'username': 'tester',
            'password': 'qwertyuiop',
            'password_conf': 'qwertyuiop',
        })
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Username is already taken!' in html
        assert 'Email is already registered!' in html

    def test_user_home(self):
        self.login()
        response = self.client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Explore' in html

    def test_guest_home(self):
        response = self.client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Explore' not in html

    def test_user_profile(self):
        self.login()
        response = self.client.get('/user/example')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Johnny Appleseed' in html
        assert 'Online' in html

    def test_edit_profile(self):
        self.login()
        response = self.client.post('/user/example', data={
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'modifiedexample',
            'headline': 'example headline',
            'about_me': 'example about me',
        },follow_redirects=True)

        assert response.status_code == 200
        assert response.request.path == '/user/modifiedexample'
        html = response.get_data(as_text=True)
        assert 'John Doe' in html
        assert 'example headline' in html
        assert 'example about me' in html

        response = self.client.get('/user/modifiedexample')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'modifiedexample' in html

    def test_invalid_login_email(self):
        response = self.client.post('/auth/login', data={
            'email': 'wrongexample@example.com',
            'password': 'qwertyuiop',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/auth/login'
        html = response.get_data(as_text=True)
        print(html)
        assert 'Email is not registered!' in html

    def test_invalid_login_password(self):
        response = self.client.post('/auth/login', data={
            'email': 'example_two@example.com',
            'password': 'asfasasdfadsf',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/auth/login'
        html = response.get_data(as_text=True)
        assert 'Incorrect password!' in html

    def test_logout(self):
        self.login()
        response = self.logout()
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Explore' not in html

    def test_invalid_edit_profile(self):
        self.login()
        response = self.client.post('/user/example', data={
            'username': 'example'
        },follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/user/example'

    def test_edit_username_duplicate(self):
        self.login(user=2)
        response = self.client.post('/user/example_two', data={
            'first_name': 'Bill',
            'last_name': 'Bob',
            'username': 'example'
        },follow_redirects=True)

        assert response.status_code == 200
        assert response.request.path == '/user/example_two'
        html = response.get_data(as_text=True)
        assert 'Bill Bob' in html
        assert 'Username is already taken!' in html

    def test_google_auth_login(self):
        pass
