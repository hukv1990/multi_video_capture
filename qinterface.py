# coding=utf-8

import logging
import time

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import numpy as np


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.widget = text_edit

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    def write(self, m):
        pass


class QThreadDisplay(QThread):
    dis_signal = pyqtSignal(object)
    def __init__(self, tid, shm_list, event_close, info_queue):
        super(QThreadDisplay, self).__init__()
        self.tid = tid
        self.shm_list = shm_list
        self.event_close = event_close
        self.info_queue = info_queue

    @staticmethod
    def _ndarray_to_pixmap(image):
        h, w, d = image.shape
        q_image = QImage(image.data, w, h, w * d, QImage.Format_BGR888)
        return QPixmap.fromImage(q_image)

    def run(self) -> None:
        while True:
            time.sleep(0.02)  # 25fps = 0.04s, 根据采样定理设置
            if self.event_close.is_set():
                self.info_queue.put(f'sub thread {[self.tid]} exit.')
                break
            if len(self.shm_list) > 0:
                image = self.shm_list[0]
                image = np.ascontiguousarray(image[:, ::-1])
                if image is None:
                    self.info_queue.put(f'[{self.tid}] image is None')
                    continue
                pixmap = self._ndarray_to_pixmap(image)
                del self.shm_list[0]
                self.dis_signal.emit(pixmap)