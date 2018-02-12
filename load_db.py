import psycopg2
import toml
import os
import pdb

def create_database(db, Config):
    if not db.table_exists('posts'):
        db.cursor.execute("CREATE TABLE posts (post_id SERIAL PRIMARY KEY, title TEXT, english TEXT, korean TEXT)")
        db.conn.commit()

    if not db.table_exists('tags'):
        db.cursor.execute("CREATE TABLE tags (tag_id SERIAL PRIMARY KEY, name TEXT)")
        db.conn.commit()

    if not db.table_exists('tag_relationships'):
        db.cursor.execute('''CREATE TABLE tag_relationships (fk_post_id SERIAL NOT NULL, 
            fk_tag_id SERIAL NOT NULL, 
            FOREIGN KEY (fk_post_id) REFERENCES posts(post_id), 
            FOREIGN KEY (fk_tag_id) REFERENCES tags(tag_id), 
            PRIMARY KEY (fk_post_id, fk_tag_id));''')
        db.conn.commit()

    if not db.table_exists('images'):
        db.cursor.execute("CREATE TABLE images (img_id SERIAL PRIMARY KEY, img_path TEXT)")
        db.conn.commit()

    if not db.table_exists('artworks'):
        db.cursor.execute('''CREATE TABLE artworks (artwork_id SERIAL PRIMARY KEY, series TEXT, 
            title TEXT, url TEXT, fk_thumbnail INT, year TEXT, materials TEXT, description TEXT, 
            FOREIGN KEY (fk_thumbnail) REFERENCES images(img_id))''')
        db.conn.commit()

    if not db.table_exists('img_relationships'):
        db.cursor.execute('''CREATE TABLE img_relationships 
            (img_relationships_id SERIAL PRIMARY KEY, fk_post_id INT, 
            fk_img_id INT, fk_artwork_id INT,
            FOREIGN KEY (fk_post_id) REFERENCES posts(post_id),
            FOREIGN KEY (fk_img_id) REFERENCES images(img_id),
            FOREIGN KEY (fk_artwork_id) REFERENCES artworks(artwork_id));''')
        db.conn.commit()


    for blog_post in os.listdir(Config.POST_DIR):
        filename = os.path.splitext(blog_post)[0]
        if '-' in filename:  # is there a better way to filter this out?
            with open(Config.POST_DIR + filename + '.toml') as conffile:   #app.listen load all posts in memory and save in object and reference dictionary
                toml_info = toml.loads(conffile.read())

                # add to database
                db.add_post(filename, toml_info['en'], toml_info['kr'])
                for image in toml_info['images']:
                    db.add_image(image)
                    db.add_image_post_relationship(filename, image)

                for tag in toml_info['tags']:
                    db.add_tag(tag)
                    db.add_tag_relationship(filename, tag)

    with open('app/content/series.toml') as conffile:
        toml_info = toml.loads(conffile.read())
        for series in toml_info:
            for artwork_title in toml_info[series]:
                artwork_info = toml_info[series][artwork_title]
                db.add_image(artwork_info['thumbnail'])
                for image in artwork_info['images']:
                    db.add_image(image)
                db.add_artwork(series, artwork_info['title'], artwork_info['url'], artwork_info['thumbnail'], artwork_info['year'], 
                    artwork_info['materials'], artwork_info['text'])
                for image in artwork_info['images']:
                    db.add_image_artwork_relationship(artwork_info['title'], image)














