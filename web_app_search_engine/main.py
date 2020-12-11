from flask import Response
from flask import request
from flask import Flask
import json
import threading
import time
import os
from google.cloud import storage
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask import render_template, flash, redirect, url_for
import os

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
index_search = {}

def list_blob_names_with_prefix(bucket_name, prefix=None):
    storage_client = storage.Client()
    if prefix == None:
        blobs = storage_client.list_blobs(bucket_name)
    else:
        blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
    blob_names = []
    for blob in blobs:
        blob_names.append(blob.name)
    return blob_names

def download_blob(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

def update_index():
    global index_search
    list_videos_processed = []
    bucket_name_tags = "datos-tarea-final-video-tags"
    while True:        
        list_videos_cloud = list_blob_names_with_prefix(bucket_name_tags)
        new_videos = list(set(list_videos_cloud) - set(list_videos_processed))
        for new_video in new_videos:
            download_blob(bucket_name_tags, new_video, "./" + new_video)
            file1 = open("./" + new_video, 'r') 
            lines = file1.readlines()
            file1.close()
            for tag in lines:
                tag = tag.strip()
                if tag in index_search:
                    index_search[tag].append(os.path.splitext(new_video)[0])
                else:
                    index_search[tag] = [os.path.splitext(new_video)[0]]
            print("INDEX =", index_search)
        list_videos_processed = list_videos_cloud
        time.sleep(3)


class UploadVideoForm(FlaskForm):
    video_file_path = StringField('Path al video:', validators=[DataRequired()])
    submit = SubmitField('Subir a la nube')

class SearchForm(FlaskForm):
    search_term = StringField('Etiqueta del video:', validators=[DataRequired()])
    submit = SubmitField('Buscar')

@app.route('/', methods=['GET', 'POST'])
def root():
    global index_search
    form1 = UploadVideoForm()
    form2 = SearchForm()
    if form1.validate_on_submit():
        video_file_path = form1.video_file_path.data
        bucket_name = "datos-tarea-final-videos"
        source_file_name = video_file_path
        destination_blob_name = os.path.basename(video_file_path)
        print("Subiendo video")
        upload_blob(bucket_name, source_file_name, destination_blob_name)
        print("Terminó de subir")
        msg = "Se subió el video"
        return render_template('index.html', form1=form1, form2=form2, msg=msg)
    elif form2.validate_on_submit():
        print(form2.search_term.data)
        result_search = index_search.get(form2.search_term.data, [])
        return render_template('index.html', form1=form1, form2=form2, result_search=result_search)
    else:
        return render_template('index.html', form1=form1, form2=form2)

if __name__ == '__main__':
    thread1 = threading.Thread(target=update_index, daemon=True)
    thread1.start()
    app.run(host='0.0.0.0', port=80, debug=True)
    #app.run(host='127.0.0.1', port=8080, debug=True)