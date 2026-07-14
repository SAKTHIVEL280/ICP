#storage place for objects that multiple files need to use.
from flask import Flask
from config import Config # for importing the config file's contents
from extensions import db,migrate,jwt # for importing the db and migrate objects from extensions.py
from models.user import User # for importing the User model from models/user.py
from models.department import Department # for importing the Department model from models/department.py
from models.category import Category # for importing the Category model from models/category.py
from models.complaint import Complaint # for importing the Complaint model from models/complaint.py
from models.comment import Comment # for importing the Comment model from models/comment.py
from models.attachment import Attachment # for importing the Attachment model from models/attachment.py
from models.complaint_history import ComplaintHistory # for importing the ComplaintHistory model from models/complaint_history.py
from models.notification import Notification # for importing the Notification model from models/notification.py
from models.activity_log import ActivityLog # for importing the ActivityLog model from models/activity_log.py
from flask_cors import CORS # for importing the CORS class from flask_cors to enable Cross-Origin Resource Sharing
from routes.auth_routes import auth_bp # for importing the auth_bp blueprint from routes/auth_routes.py
from routes.test_routes import test_bp # for importing the test_bp blueprint from routes/test_routes.py
from routes.complaint_routes import complaints_bp # for importing complaints_bp blueprint from routes/complaint_routes.py
from routes.manager_routes import manager_bp # for importing manager_bp blueprint from routes/manager_routes.py
from routes.technician_routes import technician_bp # for importing technician_bp blueprint from routes/technician_routes.py
from routes.notification_routes import notifications_bp # for importing notifications_bp blueprint from routes/notification_routes.py
from routes.report_routes import reports_bp # for importing reports_bp blueprint from routes/report_routes.py

app = Flask(__name__) # create a Flask application instance
CORS(app) # Enable CORS for all routes so the frontend can interact with the backend API
app.config.from_object(Config) # load the configuration settings from the Config class

# Register all Blueprints with their appropriate URL prefixes
app.register_blueprint(auth_bp, url_prefix="/api/auth") # set URL prefix for authentication endpoints
app.register_blueprint(test_bp, url_prefix="/api") # set URL prefix for test endpoints
app.register_blueprint(complaints_bp, url_prefix="/api/complaints") # set URL prefix for complaint endpoints
app.register_blueprint(manager_bp, url_prefix="/api/manager") # set URL prefix for department manager endpoints
app.register_blueprint(technician_bp, url_prefix="/api/technician") # set URL prefix for technician endpoints
app.register_blueprint(notifications_bp, url_prefix="/api/notifications") # set URL prefix for notification endpoints
app.register_blueprint(reports_bp, url_prefix="/api/reports") # set URL prefix for analytics reports endpoints

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