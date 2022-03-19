import time
from locust import HttpUser, task, between, constant_throughput, tag, constant
from lxml import html
import re
from web_app.models import User, Settings
from web_app import db

NUMTESTUSERS = 200
testUserNum = [x for x in range(NUMTESTUSERS, 0, -1)]


class ExampleUser(HttpUser):
    testNum = None
    wait_time = constant(1)
    username = ""
    email = ""

    def on_start(self):
        self.testNum = testUserNum.pop()
        self.username = f"loadtest{self.testNum}"
        self.email = f"loadtest{self.testNum}@resumated.com"
        self.signup()
        self.login()

    def on_stop(self):
        self.delete_user()

    def delete_user(self):
        response = self.client.get(f"/user/{self.username}")
        while 'Get personalized feedback' not in str(response.text):
            response = self.client.post('/delete_user')

    def signup(self):
        response = self.client.get('/auth/signup')
        while 'Sign in' not in str(response.text):
            result = self.client.get("/auth/signup")
            token = re.search(b'(<input id="csrf_token" name="csrf_token" type="hidden" value=")([-A-Za-z.0-9]+)', result.content)
            response = self.client.post(
                "/auth/signup",
                data={
                    "email": self.email,
                    "first_name": "Test",
                    "last_name": f"User - {self.testNum}",
                    "username": self.username,
                    "password": "qwertyuiop",
                    "password_conf": "qwertyuiop",
                    "csrf_token": token.group(2).decode("utf-8")
                },
            )

    def login(self):
        result = self.client.post("/auth/login")
        token = re.search(b'(<input id="csrf_token" name="csrf_token" type="hidden" value=")([-A-Za-z.0-9]+)', result.content)
        self.client.post(
            "/auth/login",
            data={
                "email": self.email,
                "password": "qwertyuiop",
                "csrf_token": token.group(2).decode("utf-8")
            },
        )

    @tag('explore')
    @task
    def homepage(self):
        self.client.get("/explore")

    @task
    def view_users(self):
        self.client.get("/user/caspinprince")

    @task
    def update_profile(self):
        result = self.client.get(f"/user/{self.username}")
        token = re.search(b'(<input id="csrf_token" name="csrf_token" type="hidden" value=")([-A-Za-z.0-9]+)', result.content)
        self.client.post(
            f'/user/{self.username}',
            data={
                'headline': 'example headline',
                'about_me': 'example about me',
                "csrf_token": token.group(2).decode("utf-8")
            }
        )

    @task
    def view_file_list(self):
        self.client.get(f"/user_files/{self.username}/my-files")

    @task
    def view_file(self):
        response = self.client.get("/document/7/121%20Written%20Component.pdf")

    @task
    def view_privacy(self):
        self.client.get("/privacy")

    @task
    def upload_file(self):
        headers = {'content-type': 'application/pdf'}
        result = self.client.get(f"/user_files/{self.username}/my-files")
        token = re.search(b'(<input id="csrf_token" name="csrf_token" type="hidden" value=")([-A-Za-z.0-9]+)', result.content)
        document = open('test.pdf', 'r')
        document = document.read()
        response = self.client.post(
            f"/user_files/{self.username}/my-files",
            data={
                'filename': 'testfile',
                'document': document,
                "csrf_token": token.group(2).decode("utf-8"),
                "headers": headers
            }
        )

