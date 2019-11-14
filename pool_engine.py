from gabriel_server import cognitive_engine
from gabriel_protocol import gabriel_pb2
import import pool_cv


class PoolEngine(cognitive_engine.Engine):
    def handle(self, from_client):
        if from_client.payload_type != gabriel_pb2.PayloadType.IMAGE:
            return cognitive_engine.wrong_input_format_error(
                from_client.frame_id)

        img_array = np.asarray(bytearray(from_client.payload), dtype=np.int8)
        img = cv2.imdecode(img_array, -1)

        if max(img.shape) > IMAGE_MAX_WH:
            img = cv2.resize(img, (0, 0), fx=resize_ratio, fy=resize_ratio,
                             interpolation=cv2.INTER_AREA)

        rtn_msg, objects = pc.process(img)
