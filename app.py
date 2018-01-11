#from flaskext.markdown import Markdown
from flask import Flask, request, render_template, url_for, json, redirect
from flask import Markup
from os import listdir
from os.path import isfile, join
import markdown
import toml

"""
HOW TO USE TOML
with open("conf.toml") as conffile:
    config = toml.loads(conffile.read())"""

app = Flask(__name__, static_url_path='')

@app.route('/')
def index(name=None):
	return render_template('home.html', name=name)

# about page
@app.route('/about/', methods=['GET'])
def about(name=None):
	return render_template('about.html')

# series pages consisting of a gallery of images of artwork in the series
@app.route('/series/<string:series>', methods=['GET'])
def series(series, items=None):
	print("request: " + request.referrer)
	items = []

	# get all data from the static json file
	with app.open_resource('static/data.json') as f:
		data = json.load(f)
	all_series = data['series']

	# get data from toml file
	with open("content/series.toml") as conffile:
		series_data = toml.loads(conffile.read())
	print(series_data)

	# iterate through series and get data for series matching url request
	for s in all_series:
		if s['name'] == series:
			series_data = s['artworks']
			items = [(d['href'], d['thumbnail'], d['title'], d['year']) for d in series_data] 
	return render_template('series.html', series=series, items=items)

"""artwork pages with dynamic url based on artwork title
page includes images, followed by title and explanatory text (if available)"""
@app.route('/series/<path:artwork_path>', methods=['GET'])
def artwork(artwork_path, images=None, info=None, text=''):
	series, artwork = artwork_path.split("/")
	images = []
	info = ()

	# get data from the static json file
	with app.open_resource('static/data.json') as f:
		data = json.load(f)
	all_series = data['series']

	for s in all_series:
		if s['name'] == series:
			# iterate through each artwork in the series
			for a in s['artworks']:
				# get info for artwork matching url request
				if a['href'] == artwork:
					images = a['images']
					info = (a['title'], a['materials'], a['year']) # Q: tuple vs. each as own variable?
					text = Markup(markdown.markdown(a['text']))
	return render_template('artwork.html', images=images, info=info, text=text)

# aggregated blog posts
@app.route('/blog/', methods=['GET'])
def blog(name=None, posts=None):
	post_data = []
	# iterate through text files (blogposts) in posts directory
	for post in listdir('static/posts'):
		with app.open_resource('static/posts/' + post, 'r') as f:
			content = f.read()
			post_data.append((post, content))

	return render_template('post.html', posts=post_data)

# back button goes to referring url
@app.route('/back', methods=['GET'])
def back(name=None):
	return redirect(previous_url) # helper function  (jinja macros)

# routing for external urls --> Q: is there a better way to do this?
@app.route('/external/<path:external_url>')
def external(external_url=None):
	return redirect(external_url)

