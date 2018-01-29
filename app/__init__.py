import os
import toml
import psycopg2
from flask import Flask
from urllib import parse
from config import Config
from sortedcontainers import SortedDict
from app import post, artwork, manage_posts

import load_db
import pdb


app = Flask(__name__, static_url_path='')
app.config.from_object(Config)

conn = psycopg2.connect("dbname=blog_posts user=ann host=localhost")
cur = conn.cursor()
db = manage_posts.Connection(conn, cur)
load_db.create_database(db, Config)

all_posts = SortedDict({})

db.cursor.execute("SELECT * FROM posts")
for blog_post in db.cursor.fetchall():
    filename = blog_post[1]
    tags = [t[0] for t in db.get_tags_for_post(filename)]
    all_posts[filename] = post.Post(filename, blog_post[2], blog_post[3], blog_post[4], tags)


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
from app import routes

