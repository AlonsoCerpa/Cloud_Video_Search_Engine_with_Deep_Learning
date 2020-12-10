import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize
import os
from google.cloud import storage
import requests
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
import sys

def upload_blob(bucket_name, source_file_name, destination_blob_name):
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)






        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)

        # Create new action
        openAction = QAction(QIcon('open.png'), '&Open', self)        
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open movie')
        openAction.triggered.connect(self.openFile)

        # Create exit action
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        #fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)








        self.num_consulta = 0
        self.num_max_results = 15
        self.list_buttons_videos = []

        self.setMinimumSize(QSize(1140, 740))
        self.setWindowTitle("Search Engine")

        pybutton = QPushButton('Seleccionar video', self)
        pybutton.clicked.connect(self.getfile)
        pybutton.resize(140, 32)
        pybutton.move(20, 20)

        pybutton = QPushButton('Subir video', self)
        pybutton.clicked.connect(self.upload_video_to_GCP)
        pybutton.resize(140, 32)
        pybutton.move(180, 20)

        nameLabel = QLabel(self)
        nameLabel.setText('Escriba:')
        nameLabel.move(20, 60)

        self.line = QLineEdit(self)
        self.line.resize(200, 32)
        self.line.move(80, 60)

        pybutton = QPushButton('Buscar', self)
        pybutton.clicked.connect(self.search)
        pybutton.resize(200, 32)
        pybutton.move(80, 100)





    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath())

        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())





    def play_video(self, video):
        print(video)
        self.mediaPlayer.setMedia(QUrl("https://storage.cloud.google.com/datos-tarea-final-videos/" + video + ".mp4"))
        self.playButton.setEnabled(True)

    def search(self):
        input_line = self.line.text()
        URL = "http://35.227.12.28/"
        PARAMS = {'search' : input_line}
        r = requests.get(url = URL, params = PARAMS)
        data = r.json()
        response = data["response"]
        print(response)
        y_pos = 320
        for button in self.list_buttons_videos:
            button.setParent(None)
        for video in response:
            pybutton = QPushButton(video, self)
            self.list_buttons_videos.append(pybutton)
            pybutton.clicked.connect(lambda: self.play_video(video))
            pybutton.resize(140, 32)
            pybutton.move(20, y_pos)
            pybutton.show()
            y_pos += 50

    def getfile(self):
        self.fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home/alonso/Videos', "Video files (*.mp4 *.mkv *.mov *.avi)")
        print(self.fname)

    def upload_video_to_GCP(self):
        bucket_name = "datos-tarea-final-videos"
        source_file_name = self.fname[0]
        destination_blob_name = os.path.basename(source_file_name)
        print("Subiendo video")
        upload_blob(bucket_name, source_file_name, destination_blob_name)
        print("Terminó de subir")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit( app.exec_() )