"""
Information and methods related to writing, editing, and reading blog posts
"""
from flask import Markup
from datetime import datetime
import os
import toml
import markdown

class Post:
    def __init__(self, date=None, en='', kr='', images=None, tags=None):
        self.date = date
        self.en = en
        self.kr = kr
        self.images = images
        self.tags = tags

        self.validate()
        
    def validate(self):
        """
        Check that attributes are in the correct format
        """
        try:
            date_obj = datetime.strptime(self.date, '%Y-%m-%d')
            if self.images == None:
                self.images = []
            if self.tags == None:
                self.tags = []
        except:
            raise ValueError('Date is not in the correct format: YYYY-MM-DD')
        
        if not isinstance(self.images, list):
            try:
                self.images = [image.strip() for image in self.images.split(',')]
            except:
                raise ValueError('Images must be a comma separated list')

        if not isinstance(self.tags, list):
            try:
                self.tags = [tag.strip() for tag in self.tags.split(',')]
            except:
                raise ValueError('Tags must be a comma separated list')

    def post_info_dict(self):
    	return {'date':self.date, 'en':self.en, 'kr':self.kr, 'images':self.images, 'tags':self.tags}

    def format_date_title(self):
        """convert date from YY-DD-MM to Month Date, Year (DOW)"""
        days = ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun']
        datetime_object = datetime.strptime(self.date, '%Y-%m-%d')
        day = datetime_object.weekday()
        return datetime_object.strftime('%b %d, %Y') + ' (' + days[day] + ')'

    def create_markdown(self, text):
        """convert markdown"""
        return Markup(markdown.markdown(text))

    def save_post(self, path):
        """
        Save blog post as toml file
        """
        file_path = os.path.join(path, '.toml')

        with open(path, 'w') as new_file:
            new_file.write(toml.dumps(self.post_info_dict()))
            new_file.close()

