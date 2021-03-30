export FLASK_APP=align.py
export FLASK_SECRET_KEY="ddddddddddddddddd"
export FLASK_RUN_PORT=8000
cd app
export CONFIG_PATH="../config.ini"

FLASK_ENV=development python -u -m flask run --host=0.0.0.0
