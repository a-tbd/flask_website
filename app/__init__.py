import os
import toml
import psycopg2
from flask import Flask
from urllib import parse
from config import Config
from sortedcontainers import SortedDict
from app import post, artwork, manage_posts
import load_db


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
    images = [i[0] for i in db.get_images_for_post(filename)]
    tags = [t[0] for t in db.get_tags_for_post(filename)]
    all_posts[filename] = post.Post(filename, blog_post[2], blog_post[3], images, tags)


all_artworks = SortedDict({})
db.cursor.execute("SELECT * FROM artworks")
for _, series, title, url, img_id, year, materials, desc in db.cursor.fetchall():
    if not series in all_artworks.keys():
        all_artworks[series] = {}
    thumbnail = db.get_image_by_id(img_id)[0]
    images = [i[0] for i in db.get_images_for_artwork(title)]
    print(images)
    all_artworks[series][url] = artwork.Artwork(series, title, url, thumbnail, year, materials, images, desc)
    
from app import blog_post
from app import routes