#!flask/bin/python
import os
from os import path
import json
import requests
import random
from flask import Flask, render_template, flash, abort,redirect, request,g,url_for, session, make_response, jsonify
from flask_googlemaps import GoogleMaps, Map
import google.cloud
from google.cloud import storage
import random
#from model import *
app = Flask(__name__)
app.config.from_object('config.ProductionConfig')
UPLOAD_FOLDER = '/tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
from flask import send_from_directory

from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime

import seaborn as sns
import pandas as pd
import matplotlib
matplotlib.use('PS')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Configure this environment variable via app.yaml
CLOUD_STORAGE_BUCKET = app.config['CLOUD_STORAGE_BUCKET']
CLOUD_FUNCTION_URL = app.config['CLOUD_FUNCTION_URL']
GOOGLE_MAP_KEY = app.config['GOOGLE_MAP_KEY']

GoogleMaps(app, key = GOOGLE_MAP_KEY)
CLASSES = ['Action', 'Adventure', 'Comedy',
           'Drama', 'Fantasy', 'Kids',
           'Music', 'School', 'Sci-Fi',
           'Slice of Life']

try:
    os.remove('/tmp/random_figure.jpg')
except:
    pass

markers = [
           (31.2304, 121.4737,'Hometown - Shanghai'),
		   (47.6062, -122.3321,'Now working at Seattle'),
		   (39.9042, 116.4074, "Got my bachelor's degree in Beijing"),
           (42.3601, -71.0589, "Got my master's degree in Boston")
		   ]
lat_avg = (markers[0][0] + markers[1][0])/2
lon_avg = (markers[0][1] + markers[1][1])/2
mymap = Map(
    identifier = 'view-side',
    lat = lat_avg,
    lng =  lon_avg,
    markers = markers,
    zoom = 2.0,
    style="height:450px;width:'100%',margin:0;"
)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/')
@app.route('/index')
def begin():
    return render_template('homepage.html')

@app.route('/photos')
def photos():
    return render_template('photos.html')

@app.route('/deep_learning')
def deep_learning():
    return render_template('deep_learning.html')


@app.route('/homepage')
def homepage():
    return render_template('homepage.html')


@app.route('/maps')
def maps():
    return render_template('maps.html', mymap = mymap)

@app.route('/upload/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/mnist')
def mnist():
    random_index = random.choices(range(100),k=4)
    f_path = './tmp/pic/temp.png'
    plot, prediction = serve_model_mnist(random_index)
    plot.savefig(f_path)
    return render_template('mnist.html', url = f_path, prediction = prediction)


@app.route('/anime', methods=['GET', 'POST'])
def anime():
    try:
        os.remove('/tmp/uploaded_figure.jpg')
    except:
        pass

    result = None
    uploaded = False
    random_file_name = None

    gcs = storage.Client()
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    blobs = gcs.list_blobs(CLOUD_STORAGE_BUCKET)
    fig_file_names = [blob.name for blob in blobs if 'figures/' in blob.name]

    if request.method=='POST':
	    uploaded_file = request.files['file']
	    src = '/tmp/uploaded_figure.jpg'
	    uploaded_file.save(src)
	    blob = bucket.blob(uploaded_file.filename)
	    blob.upload_from_filename(src)
	    files = {'name':uploaded_file.filename}
	    result = requests.post(CLOUD_FUNCTION_URL, json=files)
	    uploaded = True

    if not path.exists('/tmp/uploaded_figure.jpg'):
        random_file_name = random.choice(fig_file_names)
        src = '/tmp/random_figure.jpg'
        random_blob = bucket.blob(random_file_name)
        random_blob.download_to_filename(src)
        files = {'name':random_file_name}
        result = requests.post(CLOUD_FUNCTION_URL, json=files)
        uploaded = False


    r = eval(result.text.replace('\n',', '))
    d = pd.DataFrame({'class': CLASSES, 'prob':r[0][0]}).sort_values(by = 'prob', ascending = False)
    d['label'] = ['p>=0.5' if x >= 0.5 else 'p<0.5' for x in d['prob']]

    sns.set(style="whitegrid")
    f, ax = plt.subplots(figsize=(6, 4))
    sns.set_color_codes("pastel")
    p = sns.barplot(x='prob', y='class', data=d, hue='label',dodge=False)
    ax.set(xlim=(0, 1.1),
           ylabel="Genre",
           xlabel="Probability")
    ax.legend( loc="lower right", frameon=True)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: '{:.0%}'.format(x)))
    for pp in p.patches:
      p.annotate(format(pp.get_width(), '.2%'),
                 (pp.get_width() + 0.01,
                 pp.get_y() + pp.get_height() +0),
                 ha = 'left',
                 va = 'center',
                 xytext = (0, 10),
                 textcoords = 'offset points')

    sns.despine(left=True, bottom=True)
    p = p.get_figure()
    p.savefig('/tmp/result.jpg', bbox_inches='tight')
    return render_template('anime.html',
        uploaded = uploaded,
        filename_random = 'random_figure.jpg',
        filename_upload = 'uploaded_figure.jpg',
        filename_result = 'result.jpg',
        index_random = random_file_name.split('/')[1].split('.')[-2] if random_file_name is not None else None)


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
