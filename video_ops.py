# coding=utf-8

from abc import abstractmethod
from pathlib import Path

import cv2

import utils


class CameraReaderBase(object):
    def __init__(self, sn, **kwargs):
        self.cap = None
        self.sn = sn

    @property
    def info(self):
        return 'video reader'

    @abstractmethod
    def open(self):
        pass

    def is_opened(self):
        if self.cap is None:
            return False
        else:
            return self.cap.isOpened()

    @property
    def width(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def fps(self):
        return int(self.cap.get(cv2.CAP_PROP_FPS))

    def close(self):
        if self.is_opened():
            self.cap.release()

    @abstractmethod
    def read(self):
        return self.cap.read()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class CameraReaderUSB(CameraReaderBase):
    def __init__(self, instance_idx=0, show_factor=0.2, **kwargs):
        super(CameraReaderUSB, self).__init__(**kwargs)
        self.instance_idx = instance_idx

        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(self.instance_idx)
        # self.cap.set(6, cv2.VideoWriter.fourcc('H', '2', '6', '4'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.cap.set(cv2.CAP_PROP_FPS, 20)
        if not self.cap.isOpened():
            raise ValueError(f"No Camera Found: {self.instance_idx}")

    @property
    def info(self):
        return f"usb: {self.instance_idx}"


class CameraReaderRtsp(CameraReaderBase):
    def __init__(self, rtsp_addr, **kwargs):
        super(CameraReaderRtsp, self).__init__(**kwargs)
        self.rtsp_addr = rtsp_addr
        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(self.info)
        if not self.cap.isOpened():
            raise ValueError(f"No Camera Found: {self.info}")

    @property
    def info(self):
        return self.rtsp_addr


class DeviceReaderBase(object):
    def __init__(self, show_ratio=0.2, **kwargs):
        self.show_ratio = show_ratio

        self.cam_dict = {}

    def open(self):
        for cam in self.cam_dict.values():
            cam.open()

    def close(self):
        for cam in self.cam_dict.values():
            cam.close()

    def read_image(self):
        img_list = []
        for cam in self.cam_dict.values():
            ret, img = cam.read()
            if not ret:
                return []
            img_list.append(img)
        return img_list

    @property
    @abstractmethod
    def record_camera(self):
        pass

    @property
    def sn(self):
        return self.record_camera.sn


class DeviceReaderUSB(DeviceReaderBase):
    def __init__(self, dev_cfg, **kwargs):
        super(DeviceReaderUSB, self).__init__(**kwargs)
        self.cam_dict = {
            'camera': CameraReaderUSB(**dev_cfg)
        }

    @property
    def record_camera(self):
        return self.cam_dict['camera']


class DeviceReaderRTSP(DeviceReaderBase):
    def __init__(self, dev_cfg, **kwargs):
        super(DeviceReaderRTSP, self).__init__(**kwargs)
        self.cam_dict = {
            'main': CameraReaderRtsp(**dev_cfg['main']),
            'sub': CameraReaderRtsp(**dev_cfg['sub'])
        }

    def read_image(self):
        return [super(DeviceReaderRTSP, self).read_image()]

    @property
    def record_camera(self):
        return self.cam_dict['main']


class DeviceReaderUSBRSYNC(DeviceReaderBase):
    def __init__(self, dev_cfg, **kwargs):
        super(DeviceReaderUSBRSYNC, self).__init__(**kwargs)

        self.cam_dict = {}
        for cam_idx in dev_cfg['instance_idx']:
            cam_cfg = dev_cfg.copy()
            cam_cfg['instance_idx'] = cam_idx
            self.cam_dict[f'camera{cam_idx}'] = CameraReaderUSB(**cam_cfg)

    @property
    def record_camera(self):
        return list(self.cam_dict.values())[0]


class DeviceReadFactory(object):
    @staticmethod
    def create_instance(type, **kwargs) -> DeviceReaderBase:
        assert type in ['USB', 'RTSP', 'USBRSYNC']
        return eval(f'DeviceReader{type}')(kwargs)


class VideoWriter(object):
    def __init__(self, filepath, width, height, fps=20, fourcc='h264'):
        self.filepath = filepath
        self.fps = fps
        self.fourcc = fourcc
        self.width = width
        self.height = height
        self.vw = None

    def is_opened(self):
        return self.vw is not None

    def open(self):
        fourcc = cv2.VideoWriter_fourcc(*self.fourcc)
        self.vw = cv2.VideoWriter(self.filepath, fourcc, self.fps, (self.width, self.height))

    def close(self):
        if self.is_opened():
            self.vw.release()
            self.vw = None

    def write(self, image):
        self.vw.write(image)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class VideoWriterBatch(object):
    def __init__(self, cam_dev, prefix, postfix, fourcc, **kwargs):
        self.cam_dev: DeviceReaderBase = cam_dev

        self.vw_list = []
        self.prefix = prefix
        self.postfix = postfix
        self.fourcc = fourcc

    def open(self):
        for idx, cam in enumerate(self.cam_dev.cam_dict.values()):
            video_path = f"{self.prefix}_{idx:02d}{self.postfix}"
            w, h, fps = cam.width, cam.height, cam.fps
            if fps > 60:
                raise ValueError(f'fps error: {fps}')
            vw = VideoWriter(video_path, w, h, fps, self.fourcc)
            vw.open()
            self.vw_list.append(vw)

    def is_opened(self):
        return all([vw.is_opened() for vw in self.vw_list])

    def write(self, image_list):
        for vw, img in zip(self.vw_list, image_list):
            if isinstance(img, list):
                img = img[0]
            vw.write(img)

    def close(self):
        for vw in self.vw_list:
            vw.close()
            del vw

    def to_yaml(self, save_info):
        for idx in range(len(self.cam_dev.cam_dict.values())):
            video_path = f"{self.prefix}_{idx:02d}{self.postfix}"
            save_info['video_path'] = video_path
            utils.to_yaml(save_info, Path(video_path).with_suffix('.yaml'))


