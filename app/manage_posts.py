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

    def add_post(self, title, english, korean, images):
        self.cursor.execute("INSERT INTO posts (title, english, korean, images) VALUES (%s, %s, %s, %s);", (title, english, korean, images))
        self.conn.commit()

    def add_tag(self, tag):
        self.cursor.execute("INSERT INTO tags (name) VALUES (%s);", (tag,))
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

    def get_tags_for_post(self, post):
        self.cursor.execute('''SELECT name FROM relationships 
            INNER JOIN posts ON (posts.post_id = relationships.fk_post_id) 
            INNER JOIN tags ON (tags.tag_id = relationships.fk_tag_id) 
            WHERE title=%s;''', (post,))
        return self.cursor.fetchall()

    def get_posts_for_tag(self, tag):
        self.cursor.execute('''SELECT DISTINCT title, english, korean, images FROM relationships 
            INNER JOIN posts ON (posts.post_id = relationships.fk_post_id) 
            INNER JOIN tags ON (tags.tag_id = relationships.fk_tag_id) 
            WHERE name=%s''', (tag,))
        return self.cursor.fetchall()

    def add_relationship(self, title, tag):
        self.cursor.execute('''SELECT title, english, korean, images FROM relationships 
            INNER JOIN posts ON (posts.post_id = relationships.fk_post_id) 
            INNER JOIN tags ON (tags.tag_id = relationships.fk_tag_id) 
            WHERE title=%s AND name=%s;''', (title, tag))
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute('''INSERT INTO relationships (fk_post_id, fk_tag_id) 
                                SELECT p.post_id, t.tag_id FROM posts p, tags t 
                                WHERE p.title=%s AND t.name=%s;''', (title, tag))
        self.conn.commit()

    def table_exists(self, table):
        self.cursor.execute("SELECT relname FROM pg_class WHERE relname=%s;", (table,))
        return bool(self.cursor.fetchall())








