import os
import webapp2
import jinja2

from back_etc import *
from models import *
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        # set cookie for user
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        # request cookie from user
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


def permalink(self, post_id, **kw):
    # render permalink with post_id and parameters
    like_unlike = "Like"  # default Like button is 'Like'
    user = self.user
    post_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
    post = db.get(post_key)

    if not user:
        like_unlike = "Like"
    elif user.name in post.liker:
        like_unlike = "Unlike"
    else:
        liker_unlike = "Like"

    com_key = db.Key.from_path(
        'Comment_db', int(post_id), parent=comment_key())
    comment = db.get(com_key)
    comments = db.GqlQuery("SELECT * FROM Comment_db\
    WHERE relate_post='%s' ORDER BY created" % str(post.key().id()))
    return self.render(
        "permalink.html", post=post, like_unlike=like_unlike,
        comments=comments, **kw)


def blog_key(name='default'):
    # set Post key
    return db.Key.from_path('posts', name)


def comment_key(name='default'):
    return db.Key.from_path('commentdb', name)
