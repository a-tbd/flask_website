from app import app
from flask import Flask, request, render_template, url_for, redirect
import os
import toml
from sortedcontainers import SortedDict
from jinja2 import Template

from . import all_posts


@app.route('/write_post/', methods=['GET', 'POST'])
# @required_auth
def write_post():
    if request.method == 'POST':
        filename = request.form.get('date')
        if filename in all_posts:
            redirect_url = '/blog/' + filename + '/edit'
            return redirect(redirect_url)
        else:
            save_new_file(filename, request.form)
            return redirect(url_for('index'))
    return render_template('blog/write_post.html')

@app.route('/blog/<string:date>/edit/', methods=['GET', 'POST'])
# @required_auth
def edit_post(date):
    if request.method == 'POST':
        save_new_file(date, request.form)
        return redirect(url_for('index'))
    print(request)
    return render_template('blog/edit_post.html', date=date)