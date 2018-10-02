import os
import PySide
from PySide import QtGui, QtCore
import pyqtgraph as pg
from itertools import product
import sys
import pandas as pd

import numpy as np
from scipy.io import wavfile
import pygame

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from seg import segment_audio

class Label_Segments(QtGui.QMainWindow):
    consonants = ['b', 'd', 'g', 'k', 'p', 't']
    vowels = ['a', 'ae', 'e', 'i', 'o', 'u']
    CV = [''.join(cv) for cv in product(consonants, vowels)]

    def __init__(self, audio, fs):
        super(Label_Segments, self).__init__()

        self.audio = audio
        self.fs = fs
        # set central widget
        #self.widget = QtGui.QWidget()
        #self.setCentralWidget(self.widget)

        self.current_segment = 0

        self.init_ui()
        self.show()

    def init_ui(self):
        self.widget = QtGui.QWidget()
        self.setCentralWidget(self.widget)
        self.layout = QtGui.QVBoxLayout()
        self.widget.setLayout(self.layout)

        # menu bar
        self.file_menu = self.menuBar().addMenu("&File")
        open_file = QtGui.QAction("Open File", self, triggered=self.open_file)
        save_files = QtGui.QAction("Save Segments", self, triggered=self.save_segs)
        self.file_menu.addAction(open_file)

        self.play_button = QtGui.QPushButton("play")
        self.play_button.clicked.connect(self.play_sound)
        self.layout.addWidget(self.play_button)
        # self.figure = Figure()
        # self.canvas = FigureCanvas(self.figure)
        # self.layout.addWidget(self.canvas)

        self.audio_widget = Audio_Widget()
        self.layout.addWidget(self.audio_widget)

        self.button_box = QtGui.QGroupBox("phoneme labels")
        # self.button_box.setCheckable(True)
        self.button_layout = QtGui.QGridLayout()
        self.button_group = QtGui.QButtonGroup()
        self.button_group.setExclusive(True)
        self.button_group.buttonClicked.connect(self.phoneme_clicked)

        for cv, inds in zip(self.CV, product(range(len(self.consonants)), range(len(self.vowels)))):
            cv_button = QtGui.QPushButton(cv)
            cv_button.setObjectName(cv)
            cv_button.setCheckable(True)
            self.button_group.addButton(cv_button)
            self.button_layout.addWidget(cv_button, inds[0], inds[1])

        self.button_box.setLayout(self.button_layout)

        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)


    def open_file(self):
        file_n = QtGui.QFileDialog.getOpenFileName(self)
        pshift_fn = file_n[0].replace('raw','pshift')
        # hardcoded as fuck
        self.speaker_name = file_n.split(os.sep)[-3]
        print(file_n)

        self.fs, self.audio = wavfile.read(file_n[0])
        _, self.pshift = wavfile.read(pshift_fn)
        self.segments = pd.DataFrame(segment_audio(self.audio, self.fs),
                                     columns=['start', 'end'])
        self.segments['phoneme'] = ""
        self.segments['button_id'] = 0

        self.plot(0)

    def save_segs(self):
        # ya i'm hardcoding this what u want
        # TODO: Start here
        base_dir = '/home/lab/speech_recordings/{}/CV/'.format(self.speaker_name)
        os.makedirs(base_dir, exist_ok=True)
        for fn in self.CV:
            os.makedirs(base_dir+fn, exist_ok=True)

        for row in self.segments.iterrows():
            start_ind = np.floor(row['start'] * self.fs).astype(np.int)
            end_ind = np.ceil(row['end'] * self.fs).astype(np.int)
            file_ind = 0

            while os.path.exists(os.path.join(base_dir, row['cv'], row['cv']+str(file_ind)+'wav')):
                file_ind += 1

            #wavfile.write(os.path.join(base_dir, row['cv'], row['cv']+str(file_ind)+'wav'),
            #              rate=fs, data=self.)




    def play_sound(self):
        start = self.segments.loc[self.current_segment]['start']
        end = self.segments.loc[self.current_segment]['end']

        start_ind = np.floor(start * self.fs).astype(np.int)
        end_ind = np.floor(end * self.fs).astype(np.int)

        pygame.mixer.pre_init(self.fs, size=-16, channels=1)
        pygame.mixer.init()
        x = np.round(self.audio[start_ind:end_ind]*(2**16)/2).astype(np.int16)
        sound = pygame.sndarray.make_sound(x)

        sound.play()


        # P = pyaudio.PyAudio()
        # stream = P.open(rate=self.fs, format=pyaudio.paFloat32, channels=1, output=True)
        # stream.write(self.audio[start_ind:end_ind].tobytes())
        # stream.close()
        #
        # P.terminate()

    def phoneme_clicked(self, id):
        # get active button
        button = self.button_group.checkedButton()
        cv = button.objectName()

        self.segments.loc[self.current_segment,'phoneme'] = cv
        self.segments.loc[self.current_segment,'button_id'] = self.button_group.checkedId()

        print(self.segments.loc[self.current_segment])

    def switch_segment(self, direction="F"):
        # "F" orward or "B" ackwards
        if direction == "F":
            if len(self.segments)-1 <= self.current_segment:
                return
            self.current_segment += 1
        else:
            if self.current_segment <= 0:
                return
            self.current_segment -= 1

        self.plot()
        self.button_group.button(self.segments.loc[self.current_segment]['button_ind']).setDown()

    def plot(self, segment):

        self.audio_widget.clear()

        # plot data
        start = self.segments.loc[self.current_segment]['start']
        end = self.segments.loc[self.current_segment]['end']

        print(start, end)
        timeX = np.arange(start-1., end+1., 1.0 / self.fs)
        start_ind = np.floor(start*self.fs).astype(np.int)
        end_ind = start_ind + len(timeX)
        self.audio_widget.plot(timeX, self.audio[start_ind:end_ind])

        self.start_line = pg.InfiniteLine(movable=True, angle=90, pos=start, pen={'color':'g'})
        self.end_line   = pg.InfiniteLine(movable=True, angle=90, pos=end, pen={'color':'r'})

        self.start_line.sigPositionChangeFinished.connect(lambda: self.seg_changed('start'))
        self.end_line.sigPositionChangeFinished.connect(lambda: self.seg_changed('stop'))

        self.audio_widget.addItem(self.start_line)
        self.audio_widget.addItem(self.end_line)

    def seg_changed(self, which):
        if which == "start":
            self.segments.loc[self.current_segment,'start'] = self.start_line.value()
        elif which == "stop":
            self.segments.loc[self.current_segment,'stop'] = self.stop_line.value()


class Audio_Widget(pg.PlotWidget):
    def __init__(self):
        super(Audio_Widget, self).__init__()



if __name__ == '__main__':
    base_dir = '~/speech_recordings'
    fn = '/home/lab/speech_recordings/pshift/Aldis/Aldis_cv_1.wav'
    fs, data = wavfile.read(fn)
    data = data[0:fs*3]

    app = QtGui.QApplication(sys.argv)
    app.setStyle('plastique')  # Keeps some GTK errors at bay
    ex = Label_Segments(data, fs)
    sys.exit(app.exec_())