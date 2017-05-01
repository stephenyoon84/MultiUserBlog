import sys
sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from google.appengine.ext import db
from back_etc import *
from utils import *

class Post(db.Model):
    # post database - contain subject content and
    # created datetime last modified datetime
    # score and liker
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    name = db.StringProperty()
    score = db.IntegerProperty(default=0)
    liker = db.StringListProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def render(self):
        self._render_text = self.content
        return render_str("post.html", p=self)
