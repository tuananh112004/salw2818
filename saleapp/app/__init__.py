from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
import cloudinary
app = Flask(__name__)
from flask_login import LoginManager
app.config["SQLALCHEMY_DATABASE_URI"] ="mysql+pymysql://root:%s@localhost/hosp?charset=utf8mb4" % quote('cunto2004')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 3
app.secret_key='dkfd'
db = SQLAlchemy(app=app)
login = LoginManager(app=app)

cloudinary.config(
    cloud_name="dt3jshhfo",
    api_key="853628574498564",
    api_secret="oUhKCi58QTMmX6kqPF0g4H9MGdM",  # Click 'View API Keys' above to copy your API secret
    secure=True
)