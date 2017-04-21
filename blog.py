import os
import re
from string import letters
from rot13 import *
from signup import *

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(BlogHandler):
    # render mainpage.html
    def get(self):
        self.render("mainpage.html")

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    # post database - contain subject content and
    # created datetime last modified datetime
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

class BlogFront(BlogHandler):
    def get(self):
        # posts = Post.all().order('-created') # using python example
        posts = db.GqlQuery("select * from Post\
        order by created desc limit 10") # using GqlQuery example
        self.render('front.html', posts = posts)

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post)

class NewPost(BlogHandler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content)
            p.put()
            self.redirect("/blog/%s" % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)

class SignUpPage(BlogHandler):
    def get(self):
        self.render("sign_up.html")

    def post(self, error_username = "",
            error_password = "", error_verify = "",
            error_email = ""):
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
            self.render("sign_up.html", username = username, email = email,
                        error_username = error_username,
                        error_password = error_password,
                        error_verify = error_verify,
                        error_email = error_email)
        else:
            self.redirect("/blog/welcome?username=%s" % username)

class WelcomeHandler(BlogHandler):
    def get(self):
        username = self.request.get('username')
        self.render("welcome.html", username=username)


class Rot13Page(BlogHandler):
    def get(self):
        self.render("rot13_input.html")
    def post(self):
        items = self.request.get("text")
        result = ''
        for i in items:
            if i in rot13_set:
                result += rot13_set[rot13_set.index(i) + 13]
            else:
                result += i
        self.render("rot13_input.html", rot13_result = result)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/signup', SignUpPage),
                               ('/blog/welcome', WelcomeHandler),
                               ('/rot13', Rot13Page),
                               ],
                               debug=True)
