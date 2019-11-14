#
# Cloudlet Infrastructure for Mobile Computing
#   - Task Assistance
#
#   Author: Zhuo Chen <zhuoc@cs.cmu.edu>
#           Roger Iyengar <iyengar@cmu.edu>
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


from gabriel_server import cognitive_engine
from gabriel_protocol import gabriel_pb2
import numpy as np
import pool_cv
import cv2
import instruction_pb2
import logging


ENGINE_NAME = "instruction"

# Max image width and height
IMAGE_MAX_WH = 1920


logger = logging.getLogger(__name__)


class PoolEngine(cognitive_engine.Engine):
    def handle(self, from_client):
        if from_client.payload_type != gabriel_pb2.PayloadType.IMAGE:
            return cognitive_engine.wrong_input_format_error(
                from_client.frame_id)

        engine_fields = cognitive_engine.unpack_engine_fields(
            instruction_pb2.EngineFields, from_client)
        
        img_array = np.asarray(bytearray(from_client.payload), dtype=np.int8)
        img = cv2.imdecode(img_array, -1)

        if max(img.shape) > IMAGE_MAX_WH:
            resize_ratio = float(IMAGE_MAX_WH) / max(img.shape[0], img.shape[1])
            img = cv2.resize(img, (0, 0), fx=resize_ratio, fy=resize_ratio,
                             interpolation=cv2.INTER_AREA)

        result_wrapper = gabriel_pb2.ResultWrapper()
        result_wrapper.frame_id = from_client.frame_id
        result_wrapper.status = gabriel_pb2.ResultWrapper.Status.SUCCESS

        objects = pool_cv.process(img)
        if objects is not None:
            cue, CO_balls, pocket = objects

            result = gabriel_pb2.ResultWrapper.Result()
            result.payload_type = gabriel_pb2.PayloadType.TEXT
            result.engine_name = ENGINE_NAME
            speech = pool_cv.get_guidance(img, cue, CO_balls, pocket)
            logger.info(speech)
            result.payload = speech.encode(encoding="utf-8")
            result_wrapper.results.append(result)

            engine_fields.update_count += 1

        result_wrapper.engine_fields.Pack(engine_fields)

        return result_wrapper
