import sys
sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from google.appengine.ext import db
from back_etc import *
from models import *
from utils import *

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return
        permalink(self, post_id)

    def post(self, post_id):
        # post comments
        comment = self.request.get("comment")
        comments_key = db.Key.from_path(
            'Comment_db', int(post_id), parent=comment_key())
        comments = db.get(comments_key)
        post_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(post_key)

        if not self.user:
            error = "Please log in/sign up first."
            permalink(self, post_id, error_comment=error)
        elif comment:
            comments = Comment_db(
                parent=comment_key(), content=comment,
                relate_post=str(post.key().id()), name=self.user.name)
            comments.put()
            self.redirect("/blog/%s" % str(post.key().id()))
        else:
            self.redirect("/blog/%s" % str(post.key().id()))
