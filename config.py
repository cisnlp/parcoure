import os


class Config(object):
    SECRET_KEY = os.environ["FLASK_SECRET_KEY"]
    RECAPTCHA_PUBLIC_KEY = os.environ["CAPTCHA_SITE_KEY"]
    RECAPTCHA_PRIVATE_KEY = os.environ["CAPTCHA_SECRET_KEY"]
