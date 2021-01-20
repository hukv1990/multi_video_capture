# coding=utf-8
import math
import time
from datetime import datetime
from pathlib import Path

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QIcon, QImage, QPixmap, QPalette
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, QTimer
from PyQt5.Qt import Qt

from easydict import EasyDict as edict
from multiprocessing import Pool, Manager
import numpy as np
import logging

from qinterface import QPlainTextEditLogger, QThreadDisplay
from ui_main_interface import Ui_MainWindow
from video_ops import VideoReader, VideoWriter
import utils


class MainInterface(QMainWindow, Ui_MainWindow, QObject):
    def __init__(self, camera_cfg, video_cfg, **kwargs):
        super(MainInterface, self).__init__()
        self.camera_cfg = camera_cfg
        self.video_cfg = video_cfg

        self._camera_cnt = len(self.camera_cfg)
        self._label_img_views = self._camera_cnt
        self._cur_save_dict = None # {datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}

        # init_logging()
        self._init_camera_instance()
        self._set_ui()

    @classmethod
    def from_yaml(cls, filepath):
        config = edict(utils.load_yaml(filepath))
        camera_cfg = config.camera_cfg
        video_cfg = config.video_cfg
        return cls(camera_cfg, video_cfg)

    def _init_camera_instance(self):
        manager = Manager()
        self.info_queue = manager.Queue()
        self.event_cap = manager.Event()
        self.event_cap_show = manager.Event()
        self.event_cap_close = manager.Event()
        self.shm_show_lists = [manager.list() for i in range(self._camera_cnt)]
        self._cur_save_dict = manager.dict()

        self.cap_cfgs = self.camera_cfg.values()

        self.event_cap_close.clear()
        self.event_cap.clear()
        self.event_cap_show.clear()

        pool = Pool(self._camera_cnt * 2)
        for idx, cap_cfg in enumerate(self.cap_cfgs):
            manager_dict = {
                "info_queue": self.info_queue,
                'cap_close_event': self.event_cap_close,
                'save_path': self.video_cfg.save_path,
                'cap_event': self.event_cap,
                'save_dict': self._cur_save_dict,
            }
            pool.apply_async(video_cap_thread, args=(idx, cap_cfg.main, manager_dict, 'cap'))

        for idx, (shm_list, cap_cfg) in enumerate(zip(self.shm_show_lists, self.cap_cfgs)):
            manager_dict = {
                "info_queue": self.info_queue,
                'cap_close_event': self.event_cap_close,
                'shm_list': shm_list,
                'cap_event': self.event_cap_show,
            }
            pool.apply_async(video_cap_thread, args=(idx + 100, cap_cfg.sub, manager_dict, 'cap_show'))
        pool.close()
        self.pool = pool

        # th_list = []
        # for i in range(self._camera_cnt):
        #     th = threading.Thread(target=self.display, args=(i, self.shm_show_lists[i], ))
        #     th_list.append(th)
        # for th in th_list:
        #     time.sleep(0.01)
        #     th.start()
        # self.th_list = th_list


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

        self.th_list = []
        for i in range(self._camera_cnt):
            th = QThreadDisplay(i, self.shm_show_lists[i], self.event_cap_close, self.info_queue)
            th.dis_signal.connect(eval(f"self.label_img{i}").setPixmap)
            self.th_list.append(th)

        for th in self.th_list:
            th.start()

    @staticmethod
    def _ndarray_to_pixmap(image):
        h, w, d = image.shape
        q_image = QImage(image.data, w, h, w*d, QImage.Format_BGR888)
        return QPixmap.fromImage(q_image)

    def _set_video_save_dict(self):
        self._cur_save_dict['prefix'] = f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        self._cur_save_dict['id'] = self.lineEdit_id.text()
        self._cur_save_dict['mode'] = self.lineEdit_mode.text()
        self._cur_save_dict['loc'] = self.lineEdit_loc.text()

    def start_button_pressed_slot(self):
        if self.pbn_start.text() == u'开始':
            self._set_video_save_dict()
            self.event_cap.set()
            self.pbn_start.setText(u'结束')
            self.pbn_del.setEnabled(False)
            self.lineEdit_id.setEnabled(False)
            self.lineEdit_loc.setEnabled(False)
            self.lineEdit_mode.setEnabled(False)
        else:
            self.event_cap.clear()
            self.pbn_start.setText(u'开始')
            self.pbn_del.setEnabled(True)
            self.lineEdit_id.setEnabled(True)
            self.lineEdit_loc.setEnabled(True)
            self.lineEdit_mode.setEnabled(True)

    def _delete_by_prefix(self):
        prefix = self._cur_save_dict['prefix']
        video_list = Path(self.video_cfg.save_path).glob(rf"{prefix}*")
        for video_path in video_list:
            video_path:Path
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

    # def display(self, idx, image_list):
    #     while True:
    #         time.sleep(0.02)  # 25fps = 0.04s, 根据采样定理设置
    #         if self.event_cap_close.is_set():
    #             self.info_queue.put(f'sub thread {[idx]} exit.')
    #             break
    #         if len(image_list) > 0:
    #             image = image_list[0]
    #             image = np.ascontiguousarray(image[:, ::-1])
    #             if image is None:
    #                 self.info_queue.put(f'[{idx}] image is None')
    #                 continue
    #             pixmap = self._ndarray_to_pixmap(image)
    #             label_img = eval(f"self.label_img{idx}")
    #             label_img.setPixmap(pixmap)
    #             del image_list[0]
                # self.info_queue.put(f"[{idx}] show image")

    def closeEvent(self, event) -> None:
        result = QtWidgets.QMessageBox.question(self, "标题", "确认退出吗？",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            self.event_cap_close.set()
            # for th in self.th_list:
            #     th.join()
            self.event_cap.set()
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


def video_cap_thread(pid, cap_cfg, manager_dict, mode):
    info_queue = manager_dict['info_queue']

    if mode not in ['cap_show', 'cap']:
        info_queue.put(f'mode must be in [cap_show, cap]: mode={mode}')
        assert ValueError

    cap_event = manager_dict['cap_event']
    cap_close_event = manager_dict['cap_close_event']
    vr = VideoReader(**cap_cfg)

    def cap_show_video():
        shm_list: list = manager_dict['shm_list']
        vr.open()
        while True:
            if not cap_event.is_set():
                break
            if cap_close_event.is_set():
                return
            ret, image = vr.read()
            if (not ret) or (image is None):
                break
            shm_list.append(image)
        vr.close()

    def cap_video():
        cap_save_path = manager_dict['save_path']
        save_dict = manager_dict['save_dict']
        save_prefix = save_dict['prefix']
        video_path = f"{cap_save_path}/{save_prefix}_{pid:02d}.mp4"
        Path(video_path).parent.mkdir(parents=True, exist_ok=True)

        vr.open()
        vw = VideoWriter(video_path, vr.width, vr.height, vr.fps)
        vw.open()

        while True:
            if not cap_event.is_set():
                break
            if cap_close_event.is_set():
                return
            ret, image = vr.read()
            if not ret:
                vr.close()
                vw.close()
                raise ValueError(f'camera read error.')
            vw.write(image)
        vr.close()
        vw.close()

        save_info = {
            'video_path': video_path,
            'id': save_dict['id'],
            'mode': save_dict['mode'],
            'loc': save_dict['loc'],
            'camera_sn': vr.sn
        }

        utils.to_yaml(save_info, Path(video_path).with_suffix('.yaml'))
        info_queue.put(f"[{pid}] save video to {video_path}")

    while True:
        info_queue.put(f"[{pid}] waiting")
        cap_event.wait()
        info_queue.put(f"[{pid}] start to cap.")
        if cap_close_event.is_set():
            info_queue.put(f'sub process {[pid]} exit.')
            return
        try:
            eval(f"{mode}_video")()
            info_queue.put(f'[{pid}] stop.')
        except Exception as e:
            info_queue.put(f'[{pid}][Error] {e}')
