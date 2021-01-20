# coding=utf-8
import cv2


class VideoReader(object):
    def __init__(self, name, pwd, ip, codec, ch, subtype, sn,**kwargs):
        super(VideoReader, self).__init__()
        self.name = name
        self.pwd = pwd
        self.ip = ip
        self.codec = codec
        self.ch = ch
        self.subtype = subtype
        self.sn = sn

        self.cap = None

    def is_opened(self):
        if self.cap is None:
            return False
        else:
            return self.cap.isOpened()

    def open(self):
        self.cap = cv2.VideoCapture(self.rtsp)
        if not self.cap.isOpened():
            raise ValueError(f"No Camera Found: {self.rtsp}")

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

    def read(self):
        return self.cap.read()

    @property
    def rtsp(self):
        # return f"rtsp://{self.name}:{self.pwd}@{self.ip}//Streaming/Channels/{self.id}"
        # rtsp://admin:admin12345@192.168.1.155:554/h264/ch1/main/av_stream
        # rtsp://admin:admin12345@192.168.1.155:554/h264/ch1/sub/av_stream
        return f"rtsp://{self.name}:{self.pwd}@{self.ip}/{self.codec}/ch{self.ch}/{self.subtype}/av_stream"

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class VideoWriter(object):
    def __init__(self, filepath, width, height, fps=20):
        self.filepath = filepath
        self.fps = fps
        self.width = width
        self.height = height
        self.vw = None

    def open(self):
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.vw = cv2.VideoWriter(self.filepath, fourcc, self.fps, (self.width, self.height))

    def close(self):
        self.vw.release()

    def write(self, image):
        self.vw.write(image)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()