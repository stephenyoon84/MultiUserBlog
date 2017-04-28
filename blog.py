import os
import webapp2
import jinja2

from back_etc import *
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        # set cookie for user
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        # request cookie from user
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


class MainPage(BlogHandler):
    # render mainfront.html with 10 recent posts
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post\
        ORDER BY created DESC LIMIT 10")
        self.render("mainfront.html", posts=posts)


def users_key(group='default'):
    # set User key
    return db.Key.from_path('users', group)


class User(db.Model):
    # user database - contain user's name, pw hash, and email
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email=None):
        # create pw_hash
        pw_hash = make_pw_hash(name, pw)
        return User(parent=users_key(), name=name,
                    pw_hash=pw_hash, email=email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


def blog_key(name='default'):
    # set Post key
    return db.Key.from_path('posts', name)


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


class Comment_db(db.Model):
    # Comment database - content, name(author), relate_post,
    # and created datetime
    content = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    relate_post = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


def comment_key(name='default'):
    return db.Key.from_path('commentdb', name)


class BlogPosts(BlogHandler):
    # render all post order by new
    def get(self):
        posts = db.GqlQuery("select * from Post\
        order by created desc")
        self.render('blogpost.html', posts=posts)


def permalink(self, post_id, **kw):
    # render permalink with post_id and parameters
    like_unlike = "Like"  # default Like button is 'Like'
    user = self.user
    post_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
    post = db.get(post_key)

    if not user:
        like_unlike = "Like"
    elif user.name in post.liker:
        like_unlike = "Unlike"
    else:
        liker_unlike = "Like"

    com_key = db.Key.from_path(
        'Comment_db', int(post_id), parent=comment_key())
    comment = db.get(com_key)
    comments = db.GqlQuery("SELECT * FROM Comment_db\
    WHERE relate_post='%s' ORDER BY created" % str(post.key().id()))
    return self.render(
        "permalink.html", post=post, like_unlike=like_unlike,
        comments=comments, **kw)


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


class DeletePost(BlogHandler):
    # Post delete - only delete by author
    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        comments = db.GqlQuery("SELECT * FROM Comment_db\
        WHERE relate_post='%s' ORDER BY created" % str(post.key().id()))

        if not self.user:
            error = "Please log in/sign up first."
            permalink(self, post_id, error=error)
        elif self.user.name == post.name:
            post.delete()
            self.redirect("/")
        else:
            error = "You cannot delete this post."
            permalink(self, post_id, error=error)


class EditPost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        comments = db.GqlQuery("SELECT * FROM Comment_db\
        WHERE related_post='%s' ORDER BY created" % str(post.key().id()))

        if not self.user:
            error = "Please log in/sign up first."
            permalink(self, post_id, error=error)
        elif self.user.name == post.name:
            self.render('editpost.html', subject=post.subject,
                        content=post.content)
        else:
            error = "You cannot edit this post."
            permalink(self, post_id, error=error)

    def post(self, post_id):
        subject = self.request.get("subject")
        content = self.request.get("content")
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if subject and content:
            post.subject = subject
            post.content = content
            post.put()
            self.redirect("/blog/%s" % str(post.key().id()))
        else:
            subject = post.subject
            content = post.content
            error = "Subject and content, please!!"
            self.render("editpost.html", subject=subject,
                        content=content, error=error)


class DeleteComment(BlogHandler):
    # delete comment only by author
    def get(self):
        comments_id = self.request.get("com_id")
        com_key = db.Key.from_path(
            'Comment_db', int(comments_id), parent=comment_key())
        comment = db.get(com_key)
        user = self.user
        post_key = db.Key.from_path('Post', int(comment.relate_post),
                                    parent=blog_key())
        post = db.get(post_key)
        post_id = post.key().id()
        comments = db.GqlQuery("SELECT * FROM Comment_db\
        WHERE relate_post='%s' ORDER BY created" % str(post.key().id()))

        if comment.content:
            if not user:
                error = "Please log in/sign up first."
                permalink(self, post_id, error_comment=error)
            elif comment.name == user.name:
                comment.delete()
                self.redirect("/blog/%s" % str(comment.relate_post))
            else:
                error = "You cannot delete this comment."
                permalink(self, post_id, error_comment=error)
        else:
            error = "This comment no longer exists."
            permalink(self, post_id, error_comment=error)


class LikePost(BlogHandler):
    # user can like/unlike the post except post author
    def get(self):
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


class SignUpPage(BlogHandler):
    # Sign up page - validate user input and store to User db
    def get(self):
        self.render("sign_up.html")

    def post(self):
        have_error = False
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        v_username = valid_username(username)
        v_password = valid_password(password)
        v_verify = verify_password(password, verify)
        v_email = valid_email(email)

        if not (v_username and v_password and v_verify and v_email):
            if not v_username:
                error_username = "That's not a valid username."
            if not v_password:
                error_password = "That wasn't a valid password."
            if not v_verify:
                error_verify = "Your passwords didn't match."
            if not v_email:
                error_email = "That's not a valid email."
            self.render("sign_up.html", username=username, email=email,
                        error_username=error_username,
                        error_password=error_password,
                        error_verify=error_verify,
                        error_email=error_email)
        else:
            u = User.by_name(username)
            if u:
                msg = "That user already exists."
                self.render('sign_up.html', error_username=msg)
            else:
                u = User.register(username, password, email)
                u.put()

                self.login(u)
                self.redirect('/welcome')


class WelcomeHandler(BlogHandler):
    def get(self):
        if self.user:
            self.render('welcome.html', username=self.user.name)
        else:
            self.redirect('/signup')


class Login(BlogHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/welcome')
        else:
            msg = "Invalid login"
            self.render('login.html', error_login=msg)


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/login')


class Rot13Page(BlogHandler):
    def get(self):
        self.render("rot13_input.html")

    def post(self):
        items = self.request.get("text")
        result = ''
        for i in items:
            if i in rot13_set:
                result += rot13_set[rot13_set.index(i) + 13]
            else:
                result += i
        self.render("rot13_input.html", rot13_result=result)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/?', BlogPosts),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/delete/([0-9]+)', DeletePost),
                               ('/blog/editpost/([0-9]+)', EditPost),
                               ('/blog/newpost', NewPost),
                               ('/deletecomment', DeleteComment),
                               ('/likescore', LikePost),
                               ('/signup', SignUpPage),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/welcome', WelcomeHandler),
                               ('/rot13', Rot13Page),
                               ], debug=True)
