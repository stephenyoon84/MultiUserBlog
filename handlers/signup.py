import sys
sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from google.appengine.ext import db
from back_etc import *
from utils import *

class SignUpPage(BlogHandler):
    # Sign up page - validate user input and store to User db
    def get(self):
        self.render("sign_up.html")

    def post(
    self, error_username = "", error_password = "",
    error_verify = "", error_email = ""):
        have_error = False
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        v_username = valid_username(username)
        v_password = valid_password(password)
        v_verify = verify_password(password, verify)
        v_email = valid_email(email)

        if not (v_username and v_password and v_verify and v_email):
            if not v_username:
                error_username = "That's not a valid username."
            if not v_password:
                error_password = "That wasn't a valid password."
            if not v_verify:
                error_verify = "Your passwords didn't match."
            if not v_email:
                error_email = "That's not a valid email."
            self.render("sign_up.html", username=username, email=email,
                        error_username=error_username,
                        error_password=error_password,
                        error_verify=error_verify,
                        error_email=error_email)
        else:
            u = User.by_name(username)
            if u:
                msg = "That user already exists."
                self.render('sign_up.html', error_username=msg)
            else:
                u = User.register(username, password, email)
                u.put()

                self.login(u)
                self.redirect('/welcome')
