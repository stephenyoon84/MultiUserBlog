from back_etc import *
from models import *
from handlers import *
from utils import *


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/?', BlogPosts),
                               ('/blog/([0-9]+)', PostPage),
                               ('/deletepost', DeletePost),
                               ('/editpost', ToEditPost),
                               ('/blog/editpost/([0-9]+)', EditPost),
                               ('/blog/newpost', NewPost),
                               ('/deletecomment', DeleteComment),
                               ('/editcancel', CancelEdit),
                               ('/blog/([0-9]+)/likescore', LikePost),
                               ('/signup', SignUpPage),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/welcome', WelcomeHandler),
                               ('/rot13', Rot13Page),
                               ], debug=True)
