

from flask import Flask, Request, redirect, render_template
from flask_limiter import Limiter

from flask_login import LoginManager, UserMixin, login_user, logout_user
from flask_login import login_required
from flask_wtf import FlaskForm
from itsdangerous import URLSafeTimedSerializer
from wtforms import PasswordField, StringField
from fava import secrets_loader
from hashlib import sha256



#Flask-Login Login Manager
login_manager = LoginManager()


class User(UserMixin):
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user

    """
    def __init__(self,user_id,pw) -> None:
        self.user_id = user_id
        self.pw = pw


    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.user_id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.user_id

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
    

def _login_manager_setup(login_manager,fava_app,limiter):

    user_list = {
        secrets_loader.USER_LIST[0]: User(secrets_loader.USER_LIST[0],secrets_loader.USER_LIST[1])
        }
    login_manager.login_view = "/login"



    @login_manager.user_loader
    def load_user(user_id):
        
        return user_list.get(user_id)


    class LoginForm(FlaskForm):
        username = StringField('username')
        password = StringField("password")

    @fava_app.route("/login", methods=["GET", "POST"])
    @limiter.limit("3 per hour")
    def login():
        form = LoginForm()
        print(form.username.data,form.password.data)
        
        if form.validate_on_submit():
            username = sha256(str(secrets_loader.SECRET_KEY).encode("utf-8") + form.username.data.encode("utf-8")).hexdigest()
            password = sha256(str(secrets_loader.SECRET_KEY).encode("utf-8") + form.password.data.encode("utf-8")).hexdigest()
            print(user_list,username,password)
            tmp_user = user_list.get(username)
            if tmp_user:
                print(username)
                tmp_password = tmp_user.pw
                print(password)
                if password == tmp_password:
                    login_user(tmp_user,remember=False)
                    return redirect("/")
        
        return render_template("login.html",form=form)

    @fava_app.route("/logout", methods=["GET"])
    @login_required
    def logout():
        """Logout the current user."""
        logout_user()
        return redirect("/")


def init(fava_app:Flask,limiter:Limiter):
    login_manager.init_app(fava_app)
    _login_manager_setup(login_manager,fava_app,limiter)
