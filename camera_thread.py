# coding=utf-8

import time
from pathlib import Path

import utils
from video_ops import DeviceReadFactory, VideoWriter, VideoWriterBatch


#
# class CapShowBase(object):
#     def __init__(self):
#         pass
#
#
# class CapShowUSB(CapShowBase):
#     def __init__(self):
#         super(CapShowUSB, self).__init__()
#
#
# class CapShowRTSP(CapShowBase):
#     def __init__(self):
#         super(CapShowRTSP, self).__init__()
#
#
# class CapShowUSBRSYNC(CapShowBase):
#     def __init__(self):
#         super(CapShowUSBRSYNC, self).__init__()

def video_cap_thread(pid, cap_cfg, manager_dict):
    info_queue = manager_dict['info_queue']
    event_cap_save = manager_dict['event_cap_save']
    event_cap_show = manager_dict['event_cap_show']
    event_cap_close = manager_dict['event_cap_close']
    shm_list: list = manager_dict['shm_list']
    video_save_cfg = manager_dict['save_cfg']
    save_dict = manager_dict['save_dict']

    def cap_show_dev():
        vwb = None
        show_interval = cap_cfg['show_gap']
        cnt = 0

        dev = DeviceReadFactory.create_instance(**cap_cfg)
        dev.open()
        info_queue.put(f"[{pid}] camera opened.")
        while True:
            cnt += 1
            if not event_cap_show.is_set():
                break
            if event_cap_close.is_set():
                return

            image_list = dev.read_image()
            if len(image_list) == 0:
                raise ValueError('camera read error.')

            if event_cap_save.is_set():
                if (vwb is None) or (not vwb.is_opened()):
                    prefix = f"{video_save_cfg['save_root']}/{save_dict['prefix']}_{pid:02d}"
                    Path(prefix).parent.mkdir(parents=True, exist_ok=True)
                    vwb = VideoWriterBatch(dev, prefix, video_save_cfg['postfix'], video_save_cfg['fourcc'])
                    vwb.open()
                    info_queue.put(f"[{pid}] start to save.")
                else:
                    vwb.write(image_list)
            elif (vwb is not None) and vwb.is_opened():
                save_info = {
                    # 'video_path': video_path,
                    'id': save_dict['id'],
                    'mode': save_dict['mode'],
                    'loc': save_dict['loc'],
                    'camera_sn': dev.sn
                }
                # utils.to_yaml(save_info, Path(video_path).with_suffix('.yaml'))
                vwb.to_yaml(save_info)
                vwb.close()
                info_queue.put(f"[{pid}] save to file.")
                vwb = None
            else:
                pass

            if (cnt % show_interval == 0):
                for shm, img in zip(shm_list, image_list):
                    if len(shm) < 10:
                        if isinstance(img, list) and len(img) == 2:
                            shm.append(img[1])
                        else:
                            shm.append(img)

        dev.close()

    while True:
        info_queue.put(f"[{pid}] waitting.")
        event_cap_show.wait()
        info_queue.put(f"[{pid}] start to cap.")

        if event_cap_close.is_set():
            info_queue.put(f"[{pid}] exit.")
            return

        try:
            cap_show_dev()
            info_queue.put(f"[{pid}] stop.")
        except Exception as e:
            info_queue.put(f'[{pid}][Error] {e}')
            time.sleep(1)
