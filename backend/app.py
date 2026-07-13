#storage place for objects that multiple files need to use.
from flask import Flask
from config import Config # for importing the config file's contents
from extensions import db # for importing the db object from extensions.py

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route("/")
def home():
    return "Internal Complaint Portal Backend is Running!"
@app.route("/health")
def health():
    return "Health Check Passed"
if __name__ == "__main__":
    app.run(debug=True)