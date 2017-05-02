import sys
sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from google.appengine.ext import db
from back_etc import *
from utils import *

class DeletePost(BlogHandler):
    # Post delete - only delete by author
    def post(self):
        post_id = self.request.get("post_id")
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if not post:
            return self.redirect('/login')
        comments = db.GqlQuery("SELECT * FROM Comment_db\
        WHERE relate_post='%s' ORDER BY created" % str(post.key().id()))

        if not self.user:
            self.redirect("/login")
        elif self.user.name == post.name:
            post.delete()
            self.redirect("/")
        else:
            error = "You cannot delete this post."
            permalink(self, post_id, error=error)
