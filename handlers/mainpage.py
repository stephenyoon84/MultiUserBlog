import sys
sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from google.appengine.ext import db
from back_etc import *
from utils import *

class MainPage(BlogHandler):
    # render mainfront.html with 10 recent posts
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post\
        ORDER BY created DESC LIMIT 10")
        self.render("mainfront.html", posts=posts)
