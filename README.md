# MultiUserBlog
FSND-Project-MultiUserBlog

## Project Created Apr 19, 2017

* Run local host : `dev_appserver.py .`
* Deploy app to Google Cloud Platform :
    `gcloud app --project [project-name] deploy`
    in this project, project-name is fsnd-stephen-blog
* Address for the web app : https://fsnd-stephen-blog.appspot.com/

## Step
* Step 1: Create a Basic Blog
* Step 2: Add User Registration
* Step 3: Add Login
* Step 4: Add Logout
* Step 5: Add Other Features on Your Own
* Step 6: Final Touches

## Folder
* static : Contain CSS file
* templates : Contain HTML Files
* models : Contain database(db.Model)
* handlers : Contain handlers

## Files
* app.yaml
* back_etc.py : It contains back side functions
              This can import to blog.py using `from back_etc import *`
* blog.py : Main python file.
          - render HTML
          - set cookie and read cookie
          - Contain three db.Model(User, Post, and Comment_db)
            - User : User information(name, pw_hash, email)
            - Post : Posts (subject, content, name, score, liker,
                          created, last_modified)
            - Comment_db : Comment (content, name, relate_post, created)
          - Create new post, edit, delete post only by author
          - User can comment to the posts
          - Comment can delete by author
          - User can Like/Unlike posts
          - Post show how many likes they got
          - Sign up, Log in, Log out
          - Rot 13 Page
* utils.py : Contain global functions
