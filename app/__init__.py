from flask import Flask
from flask_compress import Compress
from config import Config
from flask_cors import CORS
from app import utils

app = Flask(__name__)
CORS(app) # required for Cross-origin Request Sharing
app._static_folder = "../static"
app.config.from_object(Config)
Compress(app)

utils.setup(app.config['CONFIG_PATH'])
from app import align
