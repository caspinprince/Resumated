<h1 align="center">
    <a href="https://resumated.com">
        <img src="https://github.com/caspinprince/Resumated/blob/main/web_app/static/full-logo.png" alt="Logo" height="125">
    </a>
</h1>

<h3 align="center">Document reviewing platform for resumes, applications and more...</h4>

## Table of contents
* [Overview](#overview)
* [Setup](#local-setup)

## Overview

Sign up for an account at [resumated.com](https://resumated.com)

Direct questions to [resumated.info@gmail.com](mailto:resumated.info@gmail.com)

## Local Setup

If you wish to run the app locally take the following steps:

1. Clone the repository.
```python
git clone https://github.com/caspinprince/Resumated.git 
```
2. Create the MySQL database (locally or hosted):


3. Generate [Google OAuth API keys](https://console.developers.google.com/apis/library):
   

4. Under the main folder path create a file named `.env` and insert the secrets in the following format:
```python
GOOGLE_OAUTH_CLIENT_ID='<oauth client id here>'
GOOGLE_OAUTH_CLIENT_SECRET='<oauth client secret here>'
OAUTHLIB_RELAX_TOKEN_SCOPE=True
OAUTHLIB_INSECURE_TRANSPORT=True
SQLALCHEMY_DATABASE_URI='<hosted or local sql databse uri here>'
FLASK_SECRET_KEY='<random string here>'
TEST_MYSQL_DB='<random string here>'
```
5. Download the necessary packages using `pip install -r requirements.txt`


6. [Install Redis](https://redis.io/download)


7. Open terminals
    - Run the app: `flask run`
    - Activate redis: `redis-server`
    - Start celery: `celery -A celery_worker:celery worker --loglevel=INFO`
 
   
8. App should be running locally!


9. Optional: 
    - Load test by running `locust`
    - Profile by running `python profiling.py`
    - View profiling results with `snakeviz test_results/`


