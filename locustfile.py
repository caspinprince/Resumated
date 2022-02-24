import time
from locust import HttpUser, task, between, constant_throughput
from lxml import html
import re
from web_app.models import User, Settings
from web_app import db

NUMTESTUSERS = 10
testUserNum = [x for x in range(NUMTESTUSERS, 0, -1)]


class ExampleUser(HttpUser):
    testNum = None
    wait_time = constant_throughput(0.01)

    def on_start(self):
        self.testNum = testUserNum.pop()
        print(self.testNum)
        self.signup()

        self.login()

    def on_stop(self):
        self.client.post('/delete_user')

    def signup(self):
        result = self.client.post("/auth/signup")
        token = re.search(b'(<input id="csrf_token" name="csrf_token" type="hidden" value=")([-A-Za-z.0-9]+)', result.content)
        print(token.group(2).decode("utf-8"))
        response = self.client.post(
            "/auth/signup",
            data={
                "email": f"testing{self.testNum}@resumated.com",
                "first_name": "Test",
                "last_name": f"User - {self.testNum}",
                "username": f"testaccount{self.testNum}",
                "password": "qwertyuiop",
                "password_conf": "qwertyuiop",
                "csrf_token": token.group(2).decode("utf-8")
            },
        )

    def login(self):
        result = self.client.post("/auth/login")
        token = re.search(b'(<input id="csrf_token" name="csrf_token" type="hidden" value=")([-A-Za-z.0-9]+)', result.content)
        print(token.group(2).decode("utf-8"))
        self.client.post(
            "/auth/login",
            data={
                "email": f"testing{self.testNum}@resumated.com",
                "password": "qwertyuiop",
                "csrf_token": token.group(2).decode("utf-8")
            },
        )

    @task
    def homepage(self):
        self.client.get("/explore")

    @task
    def view_users(self):
        self.client.get("/user/caspinprince")

    @task
    def update_profile(self):
        result = self.client.get(f"/user/testaccount{self.testNum}")
        token = re.search(b'(<input id="csrf_token" name="csrf_token" type="hidden" value=")([-A-Za-z.0-9]+)', result.content)
        self.client.post(
            f'/user/testaccount{self.testNum}',
            data={
                'headline': 'example headline',
                'about_me': 'example about me',
                "csrf_token": token.group(2).decode("utf-8")
            }
        )

    @task
    def view_file_list(self):
        self.client.get(f"/user_files/testaccount{self.testNum}/my-files")

    @task
    def view_file(self):
        response = self.client.get("/document/7/121%20Written%20Component.pdf")

    @task
    def view_privacy(self):
        self.client.get("/privacy")

