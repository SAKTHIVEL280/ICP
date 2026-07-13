#storage place for objects that multiple files need to use.
from flask import Flask
from config import Config # for importing the config file's contents
from extensions import db,migrate # for importing the db and migrate objects from extensions.py
from models.user import User # for importing the User model from models/user.py

app = Flask(__name__) # create a Flask application instance
app.config.from_object(Config) # load the configuration settings from the Config class

db.init_app(app) # initialize the database with the Flask application instance
migrate.init_app(app, db) # initialize the migration functionality with the Flask application instance

@app.route("/") 
def home():
    return "Internal Complaint Portal Backend is Running!"

@app.route("/health")
def health():
    return "Health Check Passed"
if __name__ == "__main__":
    app.run(debug=True)