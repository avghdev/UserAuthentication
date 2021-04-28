from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import gunicorn

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.secret_key = "Secret Key"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), nullable = False, unique = True)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return "<User %r>" % self.username


@app.route('/')
def index():
    if "username" in session:
        return render_template("welcome.html", user = session["username"])
    else:
        return render_template("login.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and (password == user.password):
            session["username"] = username
            return redirect("/")
        else:
            return render_template("login.html", error = "Invalid username or password")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return render_template("login.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.methods == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match")

        #check if user already exists
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template("signup.html", error="Username already exists!")

        new_user = User(username = username, password = password)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # add user to session
        session["username"] = username

        return redirect("/")
    else:
        return render_template("signup.html")


if __name__ == '__main__':
    db.create_all()
    app.run()
