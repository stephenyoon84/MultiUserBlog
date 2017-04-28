# this file contains functions related with
# validation and account security and etc
# use from filename import * in the main python file
import re
import random
import hashlib
import hmac
import string


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")


def valid_username(username):
    # validate username return boolean
    return USER_RE.match(username)


def valid_password(password):
    # validate password return boolean
    return PASSWORD_RE.match(password)


def valid_email(email):
    # validate email if exist return boolean
    if not email:
        return True
    else:
        return EMAIL_RE.match(email)


def verify_password(password, verify):
    # validate password matching with verify. return boolean
    return password == verify

# secret word
SECRET = 'dkssud$gktpdy.durlsms^wjdml!cjtqjsWo@qmffhrmdlqslek.'


def make_secure_val(val):
    # create secure value with user id and hash separate with '|'
    return '%s|%s' % (val, hmac.new(SECRET, val).hexdigest())


def check_secure_val(secure_val):
    # check and return user id
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


def make_salt():
    # create salt with random characters
    return ''.join(random.choice(string.letters) for x in xrange(5))


def make_pw_hash(name, pw, salt=None):
    # create password hash with user id, pw, and salt
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s|%s" % (salt, h)


def valid_pw(name, pw, pw_hash):
    # validate password return boolean
    salt = pw_hash.split('|')[0]
    return pw_hash == make_pw_hash(name, pw, salt)


# ROT13 set
rot13_set = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm']
