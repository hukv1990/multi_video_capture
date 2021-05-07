# coding=utf-8

import math
from datetime import datetime
from pathlib import Path

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QIcon, QImage, QPixmap, QPalette
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, QTimer
from PyQt5.Qt import Qt

from easydict import EasyDict as edict
from multiprocessing import Pool, Manager
import logging

from camera_thread import video_cap_thread
from qinterface import QPlainTextEditLogger, QThreadDisplay
from ui_main_interface import Ui_MainWindow
import utils
from functools import reduce


class MainInterface(QMainWindow, Ui_MainWindow, QObject):

    def __init__(self, camera_cfg, video_cfg, **kwargs):
        super(MainInterface, self).__init__()
        self.camera_cfg = camera_cfg
        self.video_cfg = video_cfg
        print(self.camera_cfg)

        self._camera_cnt = reduce(lambda x, y: x + y, [len(cam_cfg.instance_idx) for cam_cfg in self.camera_cfg.values()])
        self._label_img_views = self._camera_cnt
        self._cur_save_dict = None  # {datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}

        # init_logging()
        self._set_ui()
        self._init_camera_instance()

    @classmethod
    def from_yaml(cls, filepath):
        config = edict(utils.load_yaml(filepath))
        camera_cfg = config.camera_cfg
        video_cfg = config.video_cfg
        return cls(camera_cfg, video_cfg)

    def _init_camera_instance(self):
        manager = Manager()
        self.info_queue = manager.Queue()
        self.event_cap_save = manager.Event()
        self.event_cap_show = manager.Event()
        self.event_cap_close = manager.Event()
        self.shm_show_lists = []
        self._cur_save_dict = manager.dict()
        self.cap_cfgs = self.camera_cfg.values()

        self.event_cap_close.clear()
        self.event_cap_save.clear()
        self.event_cap_show.clear()

        pool = Pool(self._camera_cnt)
        for idx, cap_cfg in enumerate(self.cap_cfgs):
            manager_dict = {
                "info_queue": self.info_queue,
                'save_cfg': self.video_cfg,
                'event_cap_save': self.event_cap_save,
                'event_cap_show': self.event_cap_show,
                'event_cap_close': self.event_cap_close,
                'shm_list': None,
                'save_dict': self._cur_save_dict,
            }

            if cap_cfg.type == 'USBRSYNC':
                assert isinstance(cap_cfg.instance_idx, list)
                instance_cnt = len(cap_cfg.instance_idx)
                for _ in range(instance_cnt):
                    self.shm_show_lists.append(manager.list())
                manager_dict['shm_list'] = self.shm_show_lists[-instance_cnt:]

            elif cap_cfg.type in ['USB', 'RTSP']:
                assert isinstance(cap_cfg.instance_idx, int)
                self.shm_show_lists.append(manager.list())
                manager_dict['shm_list'] = self.shm_show_lists[-1]

            else:
                raise ValueError(cap_cfg.type)

            pool.apply_async(video_cap_thread, args=(idx, cap_cfg, manager_dict))

        pool.close()
        self.pool = pool

        # create thread to display
        self.th_list = []
        # for i in range(self._camera_cnt):
        qpid_cnt = 0
        for _, cap_cfg in enumerate(self.cap_cfgs):
            flip = cap_cfg['flip']
            scale_ratio = cap_cfg['scale_ratio']
            if cap_cfg.type == 'USBRSYNC':
                instance_cnt = len(cap_cfg.instance_idx)
            elif cap_cfg.type in ['USB', 'RTSP']:
                instance_cnt = 1
            else:
                instance_cnt = 0
            for _ in range(instance_cnt):
                th = QThreadDisplay(qpid_cnt, self.shm_show_lists[qpid_cnt], self.event_cap_close, self.info_queue, scale_ratio, flip)
                th.dis_signal.connect(eval(f"self.label_img{qpid_cnt}").setPixmap)
                self.th_list.append(th)
                qpid_cnt += 1
        for th in self.th_list:
            th.start()

    def _set_label_image(self):
        _palette = QPalette()
        _palette.setColor(QPalette.Background, Qt.gray)
        h = 2 if self._camera_cnt == 3 else math.floor(math.sqrt(self._camera_cnt))
        w = math.ceil(self._camera_cnt / h)

        idx = 0
        v_layout = QtWidgets.QVBoxLayout()
        for i in range(h):
            h_layout = QtWidgets.QHBoxLayout()
            for j in range(w):
                label_img = QtWidgets.QLabel(self.groupBox)
                label_img.setAutoFillBackground(True)
                label_img.setAlignment(Qt.AlignCenter)
                label_img.setPalette(_palette)
                setattr(self, f"label_img{idx}", label_img)
                idx += 1
                h_layout.addWidget(label_img)
            v_layout.addLayout(h_layout)

        self.verticalLayout_img.addLayout(v_layout, stretch=1)

    def _init_logging(self):
        formater = logging.Formatter("%(asctime)-15s: %(message)s")
        text_edit_handler = QPlainTextEditLogger(self.text_edit)
        text_edit_handler.setFormatter(formater)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formater)

        logging.getLogger().addHandler(text_edit_handler)
        logging.getLogger().addHandler(stream_handler)
        logging.getLogger().setLevel(logging.INFO)

    def _set_ui(self):
        self.setupUi(self)
        self._set_label_image()
        self.text_edit = QtWidgets.QPlainTextEdit(self.groupBox)
        self.text_edit.setReadOnly(True)
        self.text_edit.setMinimumWidth(60)
        self.verticalLayout_img.addWidget(self.text_edit)
        self.text_edit.hide()

        self.setWindowTitle(u"XFACE VIDEO")
        self.statusbar.hide()
        self.setWindowIcon(QIcon('main.ico'))

        self.pbn_start.pressed.connect(self.start_button_pressed_slot)
        self.pbn_del.pressed.connect(self.delete_button_pressed_slot)
        self.actionExit.triggered.connect(self.close)
        self.actionpreview.triggered.connect(self.preview_slot)
        self.actionshowlog.triggered.connect(self.log_show_slot)
        self.actionClearLog.triggered.connect(self.text_edit.clear)
        self.actionAbout.triggered.connect(self.about_slot)
        self.actionSetting.triggered.connect(self.open_setting_slot)

        self._init_logging()
        self.qtimer_log = QTimer(self)
        self.qtimer_log.timeout.connect(self.timer_log_slot)
        self.qtimer_log.start(200)

    @staticmethod
    def _ndarray_to_pixmap(image):
        h, w, d = image.shape
        q_image = QImage(image.data, w, h, w * d, QImage.Format_RGB888)
        return QPixmap.fromImage(q_image)

    def _set_video_save_dict(self):
        self._cur_save_dict['prefix'] = f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        self._cur_save_dict['id'] = self.lineEdit_id.text()
        self._cur_save_dict['mode'] = self.lineEdit_mode.text()
        self._cur_save_dict['loc'] = self.lineEdit_loc.text()

    def start_button_pressed_slot(self):
        if self.pbn_start.text() == u'开始':
            self._set_video_save_dict()
            self.event_cap_save.set()
            self.pbn_start.setText(u'结束')
            self.pbn_del.setEnabled(False)
            self.lineEdit_id.setEnabled(False)
            self.lineEdit_loc.setEnabled(False)
            self.lineEdit_mode.setEnabled(False)
        else:
            self.event_cap_save.clear()
            self.pbn_start.setText(u'开始')
            self.pbn_del.setEnabled(True)
            self.lineEdit_id.setEnabled(True)
            self.lineEdit_loc.setEnabled(True)
            self.lineEdit_mode.setEnabled(True)

    def _delete_by_prefix(self):
        prefix = self._cur_save_dict['prefix']
        video_list = Path(self.video_cfg.save_root).glob(rf"{prefix}*")
        for video_path in video_list:
            video_path: Path
            video_path.unlink()
            self.info_queue.put(f"delete {video_path}")
        self._cur_save_dict['prefix'] = ''

    def delete_button_pressed_slot(self):
        if self._cur_save_dict.get('prefix') is None or len(self._cur_save_dict['prefix']) == 0:
            QtWidgets.QMessageBox.warning(self, 'Warning', u'没有可删除内容', QtWidgets.QMessageBox.Yes,
                                          QtWidgets.QMessageBox.Yes)
            return

        result = QtWidgets.QMessageBox.question(self, "标题", "确认删除吗？",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            self._delete_by_prefix()

    def closeEvent(self, event) -> None:
        result = QtWidgets.QMessageBox.question(self, "标题", "确认退出吗？",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            self.event_cap_close.set()
            # for th in self.th_list:
            #     th.join()
            self.event_cap_save.set()
            self.event_cap_show.set()
            self.pool.join()
            for th in self.th_list:
                th.wait()

            event.accept()
        else:
            event.ignore()

    def preview_slot(self, status):
        if status:
            self.event_cap_show.set()
        else:
            self.event_cap_show.clear()

    def log_show_slot(self, status):
        if status:
            self.text_edit.show()
        else:
            self.text_edit.hide()

    def open_setting_slot(self, status):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('config.yaml'))

    def about_slot(self, status):
        QtWidgets.QMessageBox.about(self, 'About', f'hukv1990@gmail.com')

    def timer_log_slot(self):
        while not self.info_queue.empty():
            info = self.info_queue.get()
            logging.info(info)


