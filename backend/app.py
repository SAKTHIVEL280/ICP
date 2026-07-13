#storage place for objects that multiple files need to use.
from flask import Flask
from config import Config # for importing the config file's contents
from extensions import db,migrate,jwt # for importing the db and migrate objects from extensions.py
from models.user import User # for importing the User model from models/user.py
from models.department import Department # for importing the Department model from models/department.py
from routes.auth_routes import auth_bp # for importing the auth_bp blueprint from routes/auth_routes.py


app = Flask(__name__) # create a Flask application instance
app.config.from_object(Config) # load the configuration settings from the Config class
app.register_blueprint(auth_bp, url_prefix="/api/auth") # register the auth_bp blueprint with the Flask application instance, and set the URL prefix for all routes in this blueprint to "api/auth"
db.init_app(app) # initialize the database with the Flask application instance
migrate.init_app(app, db) # initialize the migration functionality with the Flask application instance
jwt.init_app(app) # initialize the JWT functionality with the Flask application instance
print("JWT Secret:", app.config.get("JWT_SECRET_KEY"))
print("Extensions:", app.extensions)
@app.route("/") 
def home():
    return "Internal Complaint Portal Backend is Running!"

@app.route("/health")
def health():
    return "Health Check Passed"
if __name__ == "__main__":
    app.run(debug=True)