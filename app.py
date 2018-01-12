#from flaskext.markdown import Markdown
from flask import Flask, request, render_template, url_for, json, redirect
from flask import Markup
from os import listdir
import os
from os.path import isfile, join
import markdown
import toml
from datetime import datetime
from sortedcontainers import SortedDict

all_posts = SortedDict({})

for post in listdir('content/posts'):
    filename = os.path.splitext(post)[0]
    if filename != '.DS_Store':  # is there a better way to filter this out?
        print(filename)
        with open('content/posts/' + filename + '.toml') as conffile:   #app.listen load all posts in memory and save in object and reference dictionary
            all_posts[filename] = toml.loads(conffile.read())

app = Flask(__name__, static_url_path='')

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
    with open("content/series.toml") as conffile:
        artworks = toml.loads(conffile.read())[name]
    return render_template('series.html', series=name, artworks = artworks)

@app.route('/series/<path:artwork_path>', methods=['GET'])
def artwork(artwork_path, artwork_data=None):
    """
    artwork pages with dynamic url based on artwork title
    page includes images, followed by title and explanatory text (if available)
    """
    series, name = artwork_path.split("/")

    with open("content/series.toml") as conffile:
        artwork_data = toml.loads(conffile.read())[series][name]
    return render_template('artwork.html', artwork_data=artwork_data)

@app.route('/blog/', methods=['GET'])
def blog(name=None):
    """blogroll"""
    return render_template('post.html', all_posts=all_posts)

@app.route('/blog/<string:post_date>', methods=['GET'])
def blog_post_page(post_date, content=None): 
    """blog post"""
    return render_template('single_post.html', content=all_posts[post_date])

@app.route('/blog/tag/<string:tag_name>', methods=['GET'])
def tag_page(tag_name, tagged_posts=None):
    """all posts associated with selected tag"""
    tagged_posts = SortedDict({})
    for post in all_posts:
        for tag in all_posts[post]['tags']:
            if tag == tag_name:
                tagged_posts[post] = all_posts[post]
    return render_template('post.html', all_posts=tagged_posts)

# routing for external urls --> Q: is there a better way to do this?
@app.route('/external/<path:external_url>')
def external(external_url=None):
    return redirect(external_url)

########################
### helper functions ###
########################

def create_markdown(text):
    """convert markdown"""
    return Markup(markdown.markdown(text))

def format_date(date):
    """convert date from YY-DD-MM to Month Date, Year (DOW)"""
    days = ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun']
    datetime_object = datetime.strptime(date, '%Y-%d-%m')
    day = datetime_object.weekday()
    return datetime_object.strftime('%b %d, %Y') + ' (' + days[day] + ')'

app.jinja_env.globals.update(create_markdown=create_markdown, format_date=format_date, reversed=reversed)

