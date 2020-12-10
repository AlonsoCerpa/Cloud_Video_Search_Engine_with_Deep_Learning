import cv2
import os
from os import listdir
from os.path import isfile, join
from google.cloud import storage

# requirements.txt:
# google-api-python-client
# google-cloud-storage
# opencv-python

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

def extract_images(pathIn, pathOut):
    count = 0
    vidcap = cv2.VideoCapture(pathIn)
    while True:
        vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*1000))
        success, image = vidcap.read()
        #print ('Read a new frame: ', success)
        if not success:
            break
        cv2.imwrite( pathOut + "/frame%d.jpg" % count, image)
        count = count + 1

def generate_and_upload_frames(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    file1 = event
    bucket_name_video = "datos-tarea-final-videos"
    source_blob_name = file1['name']
    destination_file_name = "/tmp/" + file1['name']

    download_blob(bucket_name_video, source_blob_name, destination_file_name)

    #print(f"Processing file: {file['name']}.")

    name_dir_frames = 'frames_' + os.path.splitext(file1['name'])[0]
    path_dir_frames = "/tmp/" + name_dir_frames
    if not os.path.exists(path_dir_frames):
        os.mkdir(path_dir_frames)
    extract_images('/tmp/' + file1['name'], path_dir_frames)

    files_frames = [f for f in listdir(path_dir_frames) if isfile(join(path_dir_frames, f))]

    bucket_name_frames = "datos-tarea-final-frames"
    for filename in files_frames:
        source_file_name = path_dir_frames + "/" + filename
        destination_blob_name = os.path.splitext(file1['name'])[0] + "/" + filename
        upload_blob(bucket_name_frames, source_file_name, destination_blob_name)

    bucket_name_videos = "datos-tarea-final-name-videos"
    destination_blob_name = os.path.splitext(file1['name'])[0] + ".txt"
    source_file_name = "/tmp/" + destination_blob_name
    f = open(source_file_name, "w")
    f.close()
    upload_blob(bucket_name_videos, source_file_name, destination_blob_name)
