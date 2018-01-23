from app import app
from flask import Flask, request, render_template, url_for, redirect, Response
import os
import toml
from sortedcontainers import SortedDict
from jinja2 import Template
from functools import wraps

from . import all_posts, all_artworks
from app.post import Post

######################
### authentication ###
######################

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == app.config.get('USER') and password == app.config.get('PASSWORD')

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

##############
### routes ###
##############

@app.route('/')
def index(name=None):
    return render_template('home.html', name=name)

# about page
@app.route('/about/', methods=['GET'])
def about(name=None):
    return render_template('about.html')

@app.route('/series/<string:name>', methods=['GET'])   
def series(name, series=None, artworks=None):
    """
    series page displaying thumbnails and titles
    of all artworks in the series
    """
    with open("app/content/series.toml") as conffile:
        artworks = toml.loads(conffile.read())[name]
    return render_template('/art/series.html', series=name, artworks = artworks)

@app.route('/series/<path:artwork_path>', methods=['GET'])
def artwork(artwork_path, artwork_data=None):
    """
    artwork pages with dynamic url based on artwork title
    page includes images, followed by title and explanatory text (if available)
    """
    series, name = artwork_path.split('/')

    return render_template('/art/artwork.html', artwork_data=all_artworks[series][name])

@app.route('/blog/', methods=['GET'])
def blog(name=None):
    """blogroll"""
    return render_template('/blog/post.html', all_posts=all_posts)

@app.route('/blog/<string:post_date>', methods=['GET'])
def blog_post_page(post_date, content=None): 
    """blog post"""
    # return render_template('/blog/single_post.html', content=all_posts[post_date])
    return render_template('/blog/single_post.html', content=all_posts)

@app.route('/blog/tag/<string:tag_name>', methods=['GET'])
def tag_page(tag_name, tagged_posts=None):
    """all posts associated with selected tag"""
    tagged_posts = SortedDict({})
    for post in all_posts:
        for tag in all_posts[post].tags:
            if tag == tag_name:
                tagged_posts[post] = all_posts[post]
    return render_template('/blog/post.html', all_posts=tagged_posts)

# routing for external urls --> Q: is there a better way to do this?
@app.route('/external/<path:external_url>')
def external(external_url=None):
    return redirect(external_url)


###############################
### put in separate module? ###
###############################

@app.route('/write_post/', methods=['GET', 'POST'])
@requires_auth
def write_post():
    if request.method == 'POST':
        filename = request.form.get('date')
        if filename in all_posts.keys():
            redirect_url = '/blog/' + filename + '/edit'
            return redirect(redirect_url)
        else:
            new_post = Post(filename, request.form.get('en'), request.form.get('kr'), 
                            request.form.get('images'), request.form.get('tags'))
            new_post.save_post(app.config.get('POST_DIR')+filename+'.toml')
            all_posts[filename] = new_post
            return redirect(url_for('blog'))
    return render_template('blog/write_post.html')

@app.route('/blog/<string:date>/edit/', methods=['GET', 'POST'])
@requires_auth
def edit_post(date, content=None):
    if request.method == 'POST':

        new_post = Post(date, request.form.get('en'), request.form.get('kr'), 
                        request.form.get('images'), request.form.get('tags'))
        new_post.save_post(app.config.get('POST_DIR')+date+'.toml')
        all_posts[date] = new_post
        return redirect(url_for('blog'))
    
    # if it's a GET request
    return render_template('blog/edit_post.html', date=date, content=all_posts[date])


##################################
### helper functions for jinja ###
##################################

app.jinja_env.globals.update(reversed=reversed)

