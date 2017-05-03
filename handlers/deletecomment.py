import sys
sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from google.appengine.ext import db
from back_etc import *
from models import *
from utils import *

class DeleteComment(BlogHandler):
    # delete comment only by author
    def get(self):
        comments_id = self.request.get("com_id")
        com_key = db.Key.from_path(
            'Comment_db', int(comments_id), parent=comment_key())
        comment = db.get(com_key)
        post_id = self.request.get("post_id")
        user = self.user
        if comment:
            if not user:
                self.redirect("/login")
            elif comment.name == user.name:
                comment.delete()
                self.redirect("/blog/%s" % str(comment.relate_post))
            else:
                error = "You cannot delete this comment."
                permalink(self, post_id, error_comment=error)
        else:
            error = "This comment no longer exists."
            permalink(self, post_id, error_comment=error)
