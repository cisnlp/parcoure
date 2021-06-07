
export FLASK_APP=align.py
export FLASK_SECRET_KEY="neverguess"
export CONFIG_PATH="config.ini"
mkdir -p logs
mkdir -p app/logs
python -u -m prepare
