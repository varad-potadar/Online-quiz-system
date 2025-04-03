from flask import Flask
from application.database import db
from application.models import User
from datetime import date
app = None

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quizdb.sqlite3"
    db.init_app(app)
    app.app_context().push()
    init_db()
    return app

def init_db():
    db.create_all()
    if not User.query.filter_by(username="admin@gmail.com").first():
        admin = User(
            username="admin@gmail.com",
            password="1234",
            fullname="Admin User",
            qualification="MS",
            dob=date(1990,1,1),
            type="admin")
        db.session.add(admin)
        db.session.commit()

app = create_app()
from application.controller import *

if __name__ == "__main__" :
    app.run()