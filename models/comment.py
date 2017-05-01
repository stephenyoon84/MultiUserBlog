import sys
sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from google.appengine.ext import db
from utils import *

class Comment_db(db.Model):
    # Comment database - content, name(author), relate_post,
    # and created datetime
    content = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    relate_post = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
