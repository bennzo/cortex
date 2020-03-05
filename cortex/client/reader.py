import struct
import gzip
import numpy as np
from pathlib import Path
from datetime import datetime

from PIL import Image

from .utils import cortex_pb2
from ..net import protocol


class Reader:
    '''
    Mind sample reader class.

    Initialized by a path to a mind sample file and parses the user information and snapshots it contains
    according to the file extension (assuming that an appropriate parser for the extension exists).

    Extending the Reader's parsing capability:
    In order for the Reader to support new sample formats a new Driver class needs to be implemented
    and match the following requirements:
        Initialization:
            - Initialized by the path to the mind sample file
                i.e 'def __init__(self, path):'
        Registration:
            - Decorated by Reader.register_driver initialized with the appropriate extension
                i.e. @Reader.register_driver('.mind')
        Interface:
            - read_user(): Reads the user information and returns a User instance as defined in '../net/protocol.py'
            - read_snapshot(): Reads a snapshot and returns a Snapshot instance as defined in '../net/protocol.py'
    '''

    drivers = {}

    def __init__(self, path, driver_type):
        self.path = Path(path)
        self.driver = Reader.drivers[driver_type](path)
        self.user = self.read_user()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.read_snapshot()
        except EOFError:
            raise StopIteration

    @staticmethod
    def register_driver(name):
        def decorator(driver):
            Reader.drivers[name] = driver
            return driver
        return decorator

    def read_user(self):
        user = self.driver.read_user()
        if not isinstance(user, protocol.User):
            raise TypeError('Unsupported User class')
        return user

    def read_snapshot(self):
        ss = self.driver.read_snapshot()
        if not isinstance(ss, protocol.Snapshot):
            raise TypeError('Unsupported Snapshot class')
        return ss


@Reader.register_driver('protobuf')
class DriverProtobuf:
    def __init__(self, path):
        self.fd = gzip.open(path, 'rb')
        self.msg_size_format = '<L'
        self.msg_size_length = struct.calcsize(self.msg_size_format)
        self.gender_enum = {0: 'm', 1: 'f', 2: 'o'}

    def __del__(self):
        self.fd.close()

    def read_user(self):
        msg_size, = struct.unpack(self.msg_size_format, self.fd.read(self.msg_size_length))
        user = cortex_pb2.User()
        user.ParseFromString(self.fd.read(msg_size))

        protocol_user = protocol.User(uid=user.user_id,
                                      name=user.username,
                                      birthday=datetime.fromtimestamp(user.birthday),
                                      gender=self.gender_enum[user.gender])
        return protocol_user

    def read_snapshot(self):
        msg_size, = struct.unpack(self.msg_size_format, self.fd.read(self.msg_size_length))
        snapshot = cortex_pb2.Snapshot()
        snapshot.ParseFromString(self.fd.read(msg_size))

        pose = protocol.Pose(translation=(snapshot.pose.translation.x,
                                          snapshot.pose.translation.y,
                                          snapshot.pose.translation.z),
                             rotation=(snapshot.pose.rotation.x,
                                       snapshot.pose.rotation.y,
                                       snapshot.pose.rotation.z,
                                       snapshot.pose.rotation.w))

        if len(snapshot.color_image.data) == 0:
            image_color = None
        else:
            image_color_arr = Image.frombytes('RGB',
                                              (snapshot.color_image.width, snapshot.color_image.height),
                                              snapshot.color_image.data)
            image_color = protocol.ImageColor(image_color_arr)

        if len(snapshot.depth_image.data) == 0:
            image_depth = None
        else:
            image_depth_arr = np.array(snapshot.depth_image.data).reshape(snapshot.depth_image.width,
                                                                          snapshot.depth_image.height)
            image_depth = protocol.ImageDepth(Image.fromarray(image_depth_arr, 'F'))

        feelings = protocol.Feelings(hunger=snapshot.feelings.hunger,
                                     thirst=snapshot.feelings.thirst,
                                     exhaustion=snapshot.feelings.exhaustion,
                                     happiness=snapshot.feelings.happiness)

        protocol_snapshot = protocol.Snapshot(datetime.fromtimestamp(snapshot.datetime/1000),
                                              pose,
                                              image_color,
                                              image_depth,
                                              feelings)
        return protocol_snapshot


