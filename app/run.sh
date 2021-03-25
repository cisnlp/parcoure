# export CAPTCHA_SECRET_KEY='6LeBoS0aAAAAAMHMED2quWHIkdNlTZ-QaNO08NhR'
export FLASK_APP=align.py
export FLASK_SECRET_KEY="ddddddddddddddddd"
# export CAPTCHA_SITE_KEY='6LeBoS0aAAAAAC74yBXu0_YPmMRSUZvG0-VF9_t6'


FLASK_ENV=development python -u -m flask run --host=0.0.0.0  #>logs/analytics.log 2>&1

