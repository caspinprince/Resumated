from locust import HttpUser, task, between, constant_throughput, tag, constant
from lxml import html
import re
from web_app.models import User, Settings
from web_app import db


class ExampleUser(HttpUser):
    testNum = None
    wait_time = constant_throughput(1)
    email = "testing1@resumated.com"
    password = "qwertyuiop"
    logged_in = False

    def on_start(self):
        self.login()

    def login(self):

        while self.logged_in == False:
            result = self.client.get("/auth/login")
            token = re.search(b'(<input id="csrf_token" name="csrf_token" type="hidden" value=")([-A-Za-z.0-9]+)', result.content)
            response = self.client.post(
                "/auth/login",
                data={
                    "email": self.email,
                    "password": self.password,
                    "csrf_token": token.group(2).decode("utf-8")
                },
            )
            if 'Matthew Zhang' in response.text:
                self.logged_in = True
        print('Matthew Zhang' in response.text)

    @tag('explore')
    @task
    def homepage(self):
        if self.logged_in:
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

