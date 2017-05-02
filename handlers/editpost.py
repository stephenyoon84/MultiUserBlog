import sys
sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from google.appengine.ext import db
from back_etc import *
from utils import *

class ToEditPost(BlogHandler):
    # Move to edit post
    def post(self):
        post_id = self.request.get("post_id")
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        comments = db.GqlQuery("SELECT * FROM Comment_db\
        WHERE related_post='%s' ORDER BY created" % str(post.key().id()))

        if not self.user:
            self.redirect("/login")
        elif self.user.name == post.name:
            self.redirect("/blog/editpost/%s" % str(post_id))
        else:
            error = "You cannot edit this post."
            permalink(self, post_id, error=error)


class EditPost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        self.render(
        'editpost.html', subject=post.subject, content=post.content,
        post_id=post.key().id())

    def post(self, post_id):
        subject = self.request.get("subject")
        content = self.request.get("content")
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not self.user:
            self.redirect("/login")
        elif not self.user.name == post.name:
            error = "You cannot edit this post."
            self.render(
            "editpost.html", subject=subject, content=content,
            error=error, post_id=post.key().id())
        else:
            if subject and content:
                post.subject = subject
                post.content = content
                post.put()
                self.redirect("/blog/%s" % str(post.key().id()))
            else:
                subject = post.subject
                content = post.content
                error = "Subject and content, please!!"
                self.render(
                "editpost.html", subject=subject, content=content,
                error=error, post_id=post.key().id())


class CancelEdit(BlogHandler):
    def get(self):
        post_id = self.request.get("post_id")
        self.redirect("/blog/%s" % str(post_id))
