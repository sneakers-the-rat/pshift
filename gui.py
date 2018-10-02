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
        self.file_menu.addAction(save_files)

        # play button
        self.play_button = QtGui.QPushButton("play")
        self.play_button.clicked.connect(self.play_sound)
        self.layout.addWidget(self.play_button)
        # self.figure = Figure()
        # self.canvas = FigureCanvas(self.figure)
        # self.layout.addWidget(self.canvas)

        self.audio_widget = Audio_Widget()
        self.layout.addWidget(self.audio_widget)

        # phoneme buttons
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
            self.button_layout.addWidget(cv_button, inds[1], inds[0])

        self.button_box.setLayout(self.button_layout)
        self.layout.addWidget(self.button_box)

        # back and forth buttons
        self.switch_layout = QtGui.QHBoxLayout()
        self.forward = QtGui.QPushButton (">")
        self.back    = QtGui.QPushButton("<")
        self.forward.clicked.connect(lambda: self.switch_segment("F"))
        self.back.clicked.connect(lambda: self.switch_segment("B"))
        self.switch_layout.addWidget(self.back)
        self.switch_layout.addWidget(self.forward)
        self.layout.addLayout(self.switch_layout)

        self.setLayout(self.layout)


    def open_file(self):
        file_n = QtGui.QFileDialog.getOpenFileName(self)[0]
        pshift_fn = file_n.replace('raw','pshift')
        # hardcoded as fuck
        self.speaker_name = file_n.split(os.sep)[-3]

        self.fs, self.audio = wavfile.read(file_n)
        _, self.pshift = wavfile.read(pshift_fn)
        self.segments = pd.DataFrame(segment_audio(self.audio, self.fs),
                                     columns=['start', 'end'])
        self.segments['phoneme'] = ""
        self.segments['button_id'] = 0

        self.current_segment = 0
        self.plot()

    def save_segs(self):
        # ya i'm hardcoding this what u want
        speaker_name, ok = QtGui.QInputDialog.getText(None, 'Enter Speaker Name', 'Enter Speaker Name')
        if ok:
            self.speaker_name = speaker_name

        raw_dir = '/home/lab/speech_recordings/raw/{}/CV/'.format(self.speaker_name)
        pshift_dir = '/home/lab/speech_recordings/pshift/{}/CV/'.format(self.speaker_name)
        try:
            os.makedirs(base_dir)
        except:
            pass
        try:
            os.makedirs(pshift_dir)
        except:
            pass
        for fn in self.CV:
            try:
                os.makedirs(raw_dir+fn)
            except:
                pass
            try:
                os.makedirs(pshift_dir + fn)
            except:
                pass

        pho_groups = self.segments.groupby('phoneme')
        for pho, group in pho_groups:
            for i, row in group.iterrows():
                start_ind = np.floor(row['start'] * self.fs).astype(np.int)
                end_ind = np.ceil(row['end'] * self.fs).astype(np.int)
                file_ind = 0
                # avoid number conflicts
                raw_fn = os.path.join(raw_dir, pho, pho+'_'+str(file_ind)+'.wav')
                while os.path.exists(raw_fn):
                    file_ind += 1
                    raw_fn = os.path.join(raw_dir, pho, pho + '_' + str(file_ind) + '.wav')
                # write raw and pshifted
                wavfile.write(raw_fn, rate=fs, data=self.audio[start_ind:end_ind])
                pshift_fn = raw_fn.replace('raw', 'pshift')
                wavfile.write(pshift_fn, rate=fs, data=self.pshift[start_ind:end_ind])






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

    def switch_segment(self, direction="F"):
        # "F" orward or "B" ackwards
        if direction == "F":
            if len(self.segments)-1 <= self.current_segment:
                return
            self.current_segment += 1
        elif direction == "B":
            if self.current_segment <= 0:
                return
            self.current_segment -= 1

        self.plot()
        button_id = self.segments.loc[self.current_segment]['button_id']
        if button_id != 0:
            button = self.button_group.button(button_id)

            button.setDown(True)

        self.play_sound()

    def plot(self):

        self.audio_widget.clear()

        # plot data
        start = self.segments.loc[self.current_segment]['start']
        end = self.segments.loc[self.current_segment]['end']


        window_expand = 0.5
        if start-window_expand<0:
            plot_start = 0.0
        else:
            plot_start = start-window_expand
        if end + window_expand > len(self.audio)*self.fs:
            plot_end = len(self.audio)*self.fs
        else:
            plot_end = end+window_expand

        timeX = np.arange(plot_start, plot_end, 1.0 / self.fs)
        start_ind = np.floor(plot_start*self.fs).astype(np.int)
        end_ind = start_ind + len(timeX)
        self.audio_widget.plot(timeX, self.audio[start_ind:end_ind])

        self.start_line = pg.InfiniteLine(movable=True, angle=90, pos=start, pen={'color':'g'})
        self.end_line   = pg.InfiniteLine(movable=True, angle=90, pos=end, pen={'color':'r'})

        self.start_line.sigPositionChangeFinished.connect(lambda: self.seg_changed('start'))
        self.end_line.sigPositionChangeFinished.connect(lambda: self.seg_changed('end'))

        self.audio_widget.addItem(self.start_line)
        self.audio_widget.addItem(self.end_line)

        self.audio_widget.setXRange(plot_start, plot_end)
        self.audio_widget.setYRange(-1.,1.)

    def seg_changed(self, which):
        if which == "start":
            self.segments.loc[self.current_segment,'start'] = self.start_line.value()
        elif which == "end":
            self.segments.loc[self.current_segment,'end'] = self.end_line.value()


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