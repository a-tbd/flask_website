from flask import Flask
from config import Config
from sortedcontainers import SortedDict
import os
import toml
from app import post, artwork
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__, static_url_path='')
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

all_posts = SortedDict({})

for blog_post in os.listdir(Config.POST_DIR):
    filename = os.path.splitext(blog_post)[0]
    if '-' in filename:  # is there a better way to filter this out?
        with open(Config.POST_DIR + filename + '.toml') as conffile:   #app.listen load all posts in memory and save in object and reference dictionary
            toml_info = toml.loads(conffile.read())
            print(toml_info['date'])
            all_posts[filename] = post.Post(filename, toml_info['en'], toml_info['kr'], toml_info['images'], toml_info['tags'])

all_artworks = SortedDict({})
with open('app/content/series.toml') as conffile:
    toml_info = toml.loads(conffile.read())
    for series in toml_info:
        all_artworks[series] = {}
        for artwork_title in toml_info[series]:
            artwork_info = toml_info[series][artwork_title]
            all_artworks[series][artwork_title] = artwork.Artwork(series, artwork_info['title'], artwork_info['thumbnail'], 
                                                   artwork_info['year'], artwork_info['materials'], artwork_info['images'], artwork_info['text'])

from app import blog_post
from app import routes, models

