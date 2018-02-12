import psycopg2

class Connection():
    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor

    def create_table(self, name, columns):
        '''
        Takes a string table name, and string of column names with the necessary details
        (e.g. type, constraints)
        '''
        self.cursor.execute("CREATE TABLE %s (%s);", (name, columns)) 
        self.conn.commit()

    def add_post(self, title, english, korean):
        if not bool(self.get_post(title)):
            self.cursor.execute("INSERT INTO posts (title, english, korean) VALUES (%s, %s, %s);", (title, english, korean))
        self.conn.commit()

    def add_tag(self, tag):
        if not bool(self.get_tag(tag)):
            self.cursor.execute("INSERT INTO tags (name) VALUES (%s);", (tag,))
        self.conn.commit()

    def add_image(self, image):
        if not bool(self.get_image(image)):
            self.cursor.execute("INSERT INTO images (img_path) VALUES (%s);", (image,))
        self.conn.commit()

    def add_artwork(self, series, title, url, thumbnail, year, materials, description):
        if not bool(self.get_artwork(title)):
            self.cursor.execute('''INSERT INTO artworks (series, title, url, fk_thumbnail, year, materials, description) 
                SELECT %s, %s, %s, i.img_id, %s, %s, %s 
                FROM images i
                WHERE i.img_path=%s;''', 
                (series, title, url, year, materials, description, thumbnail))
        self.conn.commit()

    def delete_value(self, table, condition):
        self.cursor.execute("DELETE FROM %s WHERE %s;", (table, condition))
        self.conn.commit()

    def get_post(self, title):
        self.cursor.execute("SELECT * FROM posts WHERE title=%s;", (title,))
        return self.cursor.fetchall()

    def get_tag(self, tag):
        self.cursor.execute("SELECT * FROM tags WHERE name=%s;", (tag,))
        return self.cursor.fetchall()

    def get_image(self, image):
        self.cursor.execute("SELECT * FROM images WHERE img_path=%s;", (image,))
        return self.cursor.fetchall()

    def get_image_by_id(self, img_id):
        self.cursor.execute("SELECT img_path FROM images WHERE img_id=%s;", (img_id,))
        return self.cursor.fetchall()[0]

    def get_artwork(self, title):
        self.cursor.execute("SELECT * FROM artworks WHERE title=%s;", (title,))
        return self.cursor.fetchall()

    def get_tags_for_post(self, post):
        self.cursor.execute('''SELECT name FROM tag_relationships 
            INNER JOIN posts ON (posts.post_id = tag_relationships.fk_post_id) 
            INNER JOIN tags ON (tags.tag_id = tag_relationships.fk_tag_id) 
            WHERE title=%s;''', (post,))
        return self.cursor.fetchall()

    def get_posts_for_tag(self, tag):
        self.cursor.execute('''SELECT DISTINCT title, english, korean, images FROM tag_relationships 
            INNER JOIN posts ON (posts.post_id = tag_relationships.fk_post_id) 
            INNER JOIN tags ON (tags.tag_id = tag_relationships.fk_tag_id) 
            WHERE name=%s''', (tag,))
        return self.cursor.fetchall()

    def get_images_for_post(self, post):
        self.cursor.execute('''SELECT img_path FROM img_relationships 
            INNER JOIN posts ON (posts.post_id = img_relationships.fk_post_id) 
            INNER JOIN images ON (images.img_id = img_relationships.fk_img_id) 
            WHERE title=%s;''', (post,))
        return self.cursor.fetchall()

    def get_images_for_artwork(self, artwork):
        self.cursor.execute('''SELECT img_path FROM img_relationships 
            INNER JOIN artworks ON (artworks.artwork_id = img_relationships.fk_artwork_id) 
            INNER JOIN images ON (images.img_id = img_relationships.fk_img_id) 
            WHERE artworks.title=%s;''', (artwork,))
        return self.cursor.fetchall()

    def add_tag_relationship(self, title, tag):
        self.cursor.execute('''SELECT title, english, korean FROM tag_relationships 
            INNER JOIN posts ON (posts.post_id = tag_relationships.fk_post_id) 
            INNER JOIN tags ON (tags.tag_id = tag_relationships.fk_tag_id) 
            WHERE title=%s AND name=%s;''', (title, tag))
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute('''INSERT INTO tag_relationships (fk_post_id, fk_tag_id) 
                                SELECT p.post_id, t.tag_id FROM posts p, tags t 
                                WHERE p.title=%s AND t.name=%s;''', (title, tag))
        self.conn.commit()

    def add_image_post_relationship(self, title, image):
        self.cursor.execute('''SELECT * FROM img_relationships 
            INNER JOIN posts ON (posts.post_id = img_relationships.fk_post_id) 
            INNER JOIN images ON (images.img_id = img_relationships.fk_img_id) 
            WHERE posts.title=%s AND images.img_path=%s;''', (title, image))
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute('''INSERT INTO img_relationships (fk_post_id, fk_img_id, fk_artwork_id)
                SELECT p.post_id, i.img_id, NULL FROM posts p, images i 
                WHERE p.title=%s AND i.img_path=%s;''', (title, image))
        self.conn.commit()

    def add_image_artwork_relationship(self, title, image):
        self.cursor.execute('''SELECT * FROM img_relationships 
            INNER JOIN artworks ON (artworks.artwork_id = img_relationships.fk_artwork_id)
            INNER JOIN images ON (images.img_id = img_relationships.fk_img_id) 
            WHERE artworks.title=%s AND images.img_path=%s;''', (title, image))
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute('''INSERT INTO img_relationships (fk_post_id, fk_img_id, fk_artwork_id)
                SELECT NULL, i.img_id, a.artwork_id FROM images i, artworks a
                WHERE a.title=%s AND i.img_path=%s;''', (title, image))
        self.conn.commit()

    def table_exists(self, table):
        self.cursor.execute("SELECT relname FROM pg_class WHERE relname=%s;", (table,))
        return bool(self.cursor.fetchall())








