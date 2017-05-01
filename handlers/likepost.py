import sys
sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from google.appengine.ext import db
from back_etc import *
from utils import *
from models import *

class LikePost(BlogHandler):
    # user can like/unlike the post except post author
    def post(self, post_id):
        post_id = self.request.get("post_id")
        user = self.user
        post_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(post_key)
        com_key = db.Key.from_path(
            'Comment_db', int(post_id), parent=comment_key())
        comment = db.get(com_key)
        comments = db.GqlQuery("SELECT * FROM Comment_db\
        WHERE relate_post='%s' ORDER BY created" % str(post.key().id()))

        if not user:
            error = "Please log in/sign up first."
            permalink(self, post_id, error=error)
        elif post.name == user.name:
            error = "You cannot like your own post."
            permalink(self, post_id, error=error)
        else:
            if user.name in post.liker:
                msg = "You unlike this post."
                post.score = post.score - 1
                post.liker.remove('%s' % user.name)
                post.put()
                permalink(self, post_id, error=msg)
            else:
                msg = "You like this post."
                post.score = post.score + 1
                post.liker.append('%s' % user.name)
                post.put()
                permalink(self, post_id, error=msg)
