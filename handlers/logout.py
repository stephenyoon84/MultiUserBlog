import sys
sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from google.appengine.ext import db
from back_etc import *
from utils import *

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/login')
