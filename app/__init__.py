from flask import Flask
from flask_compress import Compress
from config import Config

app = Flask(__name__)
app._static_folder = "../static"
app.config.from_object(Config)
Compress(app)
from app import align
