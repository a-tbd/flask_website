import psycopg2
import toml
import os

def create_database(db, Config):
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


    for blog_post in os.listdir(Config.POST_DIR):
        filename = os.path.splitext(blog_post)[0]
        if '-' in filename:  # is there a better way to filter this out?
            with open(Config.POST_DIR + filename + '.toml') as conffile:   #app.listen load all posts in memory and save in object and reference dictionary
                toml_info = toml.loads(conffile.read())

                # add to database
                if not bool(db.get_post(filename)):
                    db.add_post(filename, toml_info['en'], toml_info['kr'], toml_info['images'])
                    for tag in toml_info['tags']:
                        if not bool(db.get_tag(tag)):
                            db.add_tag(tag)
                        db.add_relationship(filename, tag)