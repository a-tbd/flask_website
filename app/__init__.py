from flask import Flask
from config import Config
from sortedcontainers import SortedDict
import os
import toml
from app import post, artwork, manage_posts

from urllib import parse
import psycopg2
import pdb

app = Flask(__name__, static_url_path='')
app.config.from_object(Config)

conn = psycopg2.connect("dbname=blog_posts user=ann host=localhost")
cur = conn.cursor()

db = manage_posts.Connection(conn, cur)
# pdb.set_trace()
if not db.table_exists('posts'):
    db.cursor.execute("CREATE TABLE posts (post_id SERIAL PRIMARY KEY, title TEXT, english TEXT, korean TEXT, images TEXT[])")
    db.conn.commit()

if not db.table_exists('tags'):
    db.cursor.execute("CREATE TABLE tags (tag_id SERIAL PRIMARY KEY, name TEXT)")
    db.conn.commit()

if not db.table_exists('relationships'):
    db.cursor.execute('''CREATE TABLE relationships (fk_post_id SERIAL NOT NULL, 
        fk_tag_id SERIAL NOT NULL, 
        FOREIGN KEY (fk_post_id) REFERENCES posts(post_id), 
        FOREIGN KEY (fk_tag_id) REFERENCES tags(tag_id), 
        PRIMARY KEY (fk_post_id, fk_tag_id));''')
    db.conn.commit()
# conn = sqlite3.connect(Config.DATABASE_NAME + '.db')

all_posts = SortedDict({})

for blog_post in os.listdir(Config.POST_DIR):
    filename = os.path.splitext(blog_post)[0]
    if '-' in filename:  # is there a better way to filter this out?
        with open(Config.POST_DIR + filename + '.toml') as conffile:   #app.listen load all posts in memory and save in object and reference dictionary
            toml_info = toml.loads(conffile.read())
            print(toml_info['date'])

            # add to database
            if not bool(db.get_post(filename)):
                db.add_post(filename, toml_info['en'], toml_info['kr'], toml_info['images'])
                for tag in toml_info['tags']:
                    if not bool(db.get_tag(tag)):
                        db.add_tag(tag)
                    db.add_relationship(filename, tag)



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
from app import routes

