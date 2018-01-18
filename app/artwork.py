"""
Information and methods related to artworks
"""
from flask import Markup
import os
import toml
import markdown

class Artwork:
    def __init__(self, series=None, title=None, thumbnail=None, year=None, materials=None, images=None, text=None):
        self.series = series
        self.title = title
        self.thumbnail = thumbnail
        self.year = year
        self.materials = materials
        self.images = images
        self.text = text

        # self.validate()

    def create_markdown(self, text):
        """convert markdown"""
        return Markup(markdown.markdown(text))

