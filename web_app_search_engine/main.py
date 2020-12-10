from flask import Response
from flask import request
from flask import Flask
import json
import threading
import time
import os
from google.cloud import storage

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

app = Flask(__name__)
index_search = {}

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

@app.route('/')
def root():
    global index_search
    response = index_search.get(request.args['search'])
    if response == None:
        response = []
    data = {
        'response' : response
    }
    #print(data)
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

if __name__ == '__main__':
    thread1 = threading.Thread(target=update_index, daemon=True)
    thread1.start()
    app.run(host='0.0.0.0', port=80, debug=True)
    #app.run(host='127.0.0.1', port=8080, debug=True)