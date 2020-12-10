import cv2
import time
import os
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
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

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

# List directories
list_videos_processed = []
bucket_name_videos = "datos-tarea-final-name-videos"

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
predictor = DefaultPredictor(cfg)
classes = MetadataCatalog.get(cfg.DATASETS.TRAIN[0]).thing_classes

while True:
    list_videos_cloud = list_blob_names_with_prefix(bucket_name_videos)
    print(list_videos_cloud)

    new_videos = list(set(list_videos_cloud) - set(list_videos_processed))

    for new_video in new_videos:
        name_video = os.path.splitext(new_video)[0]
        bucket_name_frames = "datos-tarea-final-frames"
        list_frames = list_blob_names_with_prefix(bucket_name_frames, name_video)
        print(list_frames)

        set_tags_video = set()

        for frame in list_frames:
            frame_local_path = "./" + os.path.basename(frame)
            download_blob(bucket_name_frames, frame, frame_local_path)

            im = cv2.imread(frame_local_path)

            outputs = predictor(im)

            pred_classes = outputs["instances"].pred_classes
            scores = outputs["instances"].scores
            i = 0
            for pred_class in pred_classes:
                #print(classes[pred_class])
                if scores[i] > 0.85:
                    set_tags_video.add(classes[pred_class])
                i += 1

            #print(outputs["instances"].pred_classes)
            #print(outputs["instances"].pred_boxes)
            #print(classes)
            #print(outputs["instances"].scores)

        print(set_tags_video)

        source_file_name = "./tags.txt"
        f = open(source_file_name, "w")
        for tag in set_tags_video:
            f.write(tag + "\n")
        f.close()
        bucket_name_tags = "datos-tarea-final-video-tags"
        destination_blob_name = new_video
        upload_blob(bucket_name_tags, source_file_name, destination_blob_name)

    list_videos_processed = list_videos_cloud

    time.sleep(1)