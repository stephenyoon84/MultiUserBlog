import sys
sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from google.appengine.ext import db
from back_etc import *
from utils import *

class BlogPosts(BlogHandler):
    # render all post order by new
    def get(self):
        posts = db.GqlQuery("select * from Post\
        order by created desc")
        self.render('blogpost.html', posts=posts)
