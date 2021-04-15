# coding=utf-8

from abc import abstractmethod
import cv2


class VideoReaderBase(object):
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


class CameraReaderUSB(VideoReaderBase):
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


class CameraReaderRtsp(VideoReaderBase):
    def __init__(self, rtsp_addr, **kwargs):
        super(CameraReaderRtsp, self).__init__(**kwargs)
        # self.name = name
        # self.pwd = pwd
        # self.ip = ip
        # self.port = port
        # self.codec = codec
        # self.ch = ch
        # self.subtype = subtype
        self.rtsp_addr = rtsp_addr

        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(self.info)
        if not self.cap.isOpened():
            raise ValueError(f"No Camera Found: {self.info}")

    @property
    def info(self):
        # rtsp://admin@192.168.1.58:554/main/realmonitor?channel=1_subgtype=0
        # return f"rtsp://{self.name}:{self.pwd}@{self.ip}:{self.port}/{self.codec}/ch{self.ch}/{self.subtype}/av_stream"
        return self.rtsp_addr


class DeviceReaderBase(object):
    def __init__(self, show_ratio=0.2, **kwargs):
        self.show_ratio = show_ratio


class DeviceReaderUSB(DeviceReaderBase):
    def __init__(self, dev_cfg, **kwargs):
        super(DeviceReaderUSB, self).__init__(**kwargs)
        self.camera = CameraReaderUSB(**dev_cfg)

    def open(self):
        return self.camera.open()

    def close(self):
        return self.camera.close()

    def read_image(self):
        ret, image = self.camera.read()
        if not ret:
            return None, None
        return image, image

    @property
    def sn(self):
        return self.camera.sn


class DeviceReaderRTSP(DeviceReaderBase):
    def __init__(self, dev_cfg, **kwargs):
        super(DeviceReaderRTSP, self).__init__(**kwargs)
        self.main_camera = CameraReaderRtsp(**dev_cfg['main'])
        self.sub_camera = CameraReaderRtsp(**dev_cfg['sub'])

    def open(self):
        self.main_camera.open()
        self.sub_camera.open()

    def close(self):
        self.main_camera.close()
        self.sub_camera.close()

    def read_image(self):
        _, image = self.main_camera.read()
        _, image_show = self.sub_camera.read()
        return image, image_show

    @property
    def sn(self):
        return self.main_camera.sn


class DeviceReadFactory(object):
    @staticmethod
    def create_instance(type, **kwargs) -> DeviceReaderUSB:
        assert type in ['USB', 'RTSP']
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
