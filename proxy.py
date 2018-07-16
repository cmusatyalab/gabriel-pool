#!/usr/bin/env python
#
# Cloudlet Infrastructure for Mobile Computing
#   - Task Assistance
#
#   Author: Zhuo Chen <zhuoc@cs.cmu.edu>
#
#   Copyright (C) 2011-2013 Carnegie Mellon University
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import cv2
import json
import multiprocessing
import os
import pprint
import Queue
import sys
import threading
import time

if os.path.isdir("../../gabriel/server"):
    sys.path.insert(0, "../../gabriel/server")
import gabriel
import gabriel.proxy
LOG = gabriel.logging.getLogger(__name__)

sys.path.insert(0, "..")
import config
import zhuocv as zc
import pool_cv as pc

config.setup(is_streaming = True)
pc.set_config(is_streaming = True)

display_list = config.DISPLAY_LIST_STREAM

LOG_TAG = "POOL Proxy: "


class PoolProxy(gabriel.proxy.CognitiveProcessThread):
    def __init__(self, image_queue, output_queue, engine_id, log_flag = True):
        super(PoolProxy, self).__init__(image_queue, output_queue, engine_id)
        self.log_flag = log_flag

    def __repr__(self):
        return "Lego Proxy"

    def terminate(self):
        super(PoolProxy, self).terminate()

    def handle(self, header, data):
        #LOG.info("received new image")
        result = {'status' : "nothing"} # default

        ## preprocessing of input image
        img = zc.raw2cv_image(data)
        if max(img.shape) > config.IMAGE_MAX_WH:
            resize_ratio = float(config.IMAGE_MAX_WH) / max(img.shape[0], img.shape[1])
            img = cv2.resize(img, (0, 0), fx = resize_ratio, fy = resize_ratio, interpolation = cv2.INTER_AREA)
        zc.check_and_display('input', img, display_list, resize_max = config.DISPLAY_MAX_PIXEL, wait_time = config.DISPLAY_WAIT_TIME)

        ## process the image
        rtn_msg, objects = pc.process(img, display_list)
        ## for measurement, when the sysmbolic representation has been got
        if gabriel.Debug.TIME_MEASUREMENT:
            result[gabriel.Protocol_measurement.JSON_KEY_APP_SYMBOLIC_TIME] = time.time()

        if rtn_msg['status'] == 'success':
            result['status'] = 'success'
            cue, CO_balls, pocket = objects
            result['speech'] = pc.get_guidance(img, cue, CO_balls, pocket, display_list)

        header['status'] = result.pop('status')
        header[gabriel.Protocol_measurement.JSON_KEY_APP_SYMBOLIC_TIME] = result.pop(gabriel.Protocol_measurement.JSON_KEY_APP_SYMBOLIC_TIME, -1)

        return json.dumps(result)

if __name__ == "__main__":
    settings = gabriel.util.process_command_line(sys.argv[1:])

    ip_addr, port = gabriel.network.get_registry_server_address(settings.address)
    service_list = gabriel.network.get_service_list(ip_addr, port)
    LOG.info("Gabriel Server :")
    LOG.info(pprint.pformat(service_list))

    video_ip = service_list.get(gabriel.ServiceMeta.VIDEO_TCP_STREAMING_IP)
    video_port = service_list.get(gabriel.ServiceMeta.VIDEO_TCP_STREAMING_PORT)
    ucomm_ip = service_list.get(gabriel.ServiceMeta.UCOMM_SERVER_IP)
    ucomm_port = service_list.get(gabriel.ServiceMeta.UCOMM_SERVER_PORT)

    # image receiving thread
    image_queue = Queue.Queue(gabriel.Const.APP_LEVEL_TOKEN_SIZE)
    print "TOKEN SIZE OF OFFLOADING ENGINE: %d" % gabriel.Const.APP_LEVEL_TOKEN_SIZE
    video_streaming = gabriel.proxy.SensorReceiveClient((video_ip, video_port), image_queue)
    video_streaming.start()
    video_streaming.isDaemon = True

    # app proxy
    result_queue = multiprocessing.Queue()

    app_proxy = PoolProxy(image_queue, result_queue, engine_id = "Pool")
    app_proxy.start()
    app_proxy.isDaemon = True

    # result pub/sub
    result_pub = gabriel.proxy.ResultPublishClient((ucomm_ip, ucomm_port), result_queue)
    result_pub.start()
    result_pub.isDaemon = True

    try:
        while True:
            time.sleep(1)
    except Exception as e:
        pass
    except KeyboardInterrupt as e:
        LOG.info("user exits\n")
    finally:
        if video_streaming is not None:
            video_streaming.terminate()
        if app_proxy is not None:
            app_proxy.terminate()
        result_pub.terminate()

