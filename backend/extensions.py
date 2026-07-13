# This file is for initializing the database and migration objects that will be used across the application.
from flask_sqlalchemy import SQLAlchemy # for importing the SQLAlchemy class from flask_sqlalchemy
from flask_migrate import Migrate # for importing the Migrate class from flask_migrate

db = SQLAlchemy() # create an instance of the SQLAlchemy class, which will be used to interact with the database
migrate = Migrate() # create an instance of the Migrate class, which will be used to handle database migrations