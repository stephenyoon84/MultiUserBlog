import sys
sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from google.appengine.ext import db
from back_etc import *
from models.post import *
from utils import *

class NewPost(BlogHandler):
    # post new post to the blog store in Post
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if not self.user:
            error = "Please log in/sign up first."
            self.render("newpost.html", subject=subject,
                        content=content, error=error)

        elif subject and content:
            p = Post(
                parent=blog_key(), subject=subject,
                content=content, name=self.user.name)
            p.put()
            self.redirect("/blog/%s" % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject,
                        content=content, error=error)
