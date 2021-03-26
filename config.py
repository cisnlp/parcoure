import os


class Config(object):
    
    # RECAPTCHA_PUBLIC_KEY = os.environ["CAPTCHA_SITE_KEY"]
    # RECAPTCHA_PRIVATE_KEY = os.environ["CAPTCHA_SECRET_KEY"]
    CONFIG_PATH = os.environ['CONFIG_PATH']
    SECRET_KEY = os.environ["FLASK_SECRET_KEY"]