import struct
import gzip
import numpy as np
import pytz
from pathlib import Path
from datetime import datetime, timezone

from PIL import Image

from .utils import cortex_pb2
from ..net import protocol


_LOCAL_TZ = pytz.timezone('Israel')


class Reader:
    """A Reader for sample files.

    Initialized by a path to a mind sample file and parses the user information and snapshots it contains
    according to the file extension (assuming an appropriate parser for the extension exists).

    Note:
        Extending the Reader's parsing capability:\n
        In order for the Reader to support new sample formats a new Driver class needs to be implemented
        and match the following requirements:
            Initialization
                - Initialized by the path to the mind sample file.
            Registration
                - Decorated by :meth:`register_driver` initialized with the appropriate extension.
            Interface
                - read_user(): Reads the user information and returns a :class:`cortex.net.protocol.User` instance.
                - read_snapshot(): Reads a snapshot and returns a :class:`cortex.net.protocol.Snapshot` instance.

    Args:
        path (:obj:`str`): Path to the sample file
        driver_type (:obj:`str`): Identifier for the appropriate format parser
    """

    _DRIVERS = {}

    def __init__(self, path, driver_type):
        self.path = Path(path)
        self.driver = Reader._DRIVERS[driver_type](path)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.read_snapshot()
        except EOFError:
            raise StopIteration

    @staticmethod
    def register_driver(name):
        """A Decorator for registering driver classes.

        Args:
            name (:obj:`str`): The name of the registered driver
        """
        def decorator(driver):
            Reader._DRIVERS[name] = driver
            return driver
        return decorator

    def read_user(self):
        """ Reads a user from the sample file.

        Returns:
            user (:class:`cortex.net.protocol.User`)
        """
        user = self.driver.read_user()
        if not isinstance(user, protocol.User):
            raise TypeError('Unsupported User class')
        return user

    def read_snapshot(self):
        """ Reads a snapshot from the sample file.

        Returns:
            user (:class:`cortex.net.protocol.Snapshot`)
        """
        ss = self.driver.read_snapshot()
        if not isinstance(ss, protocol.Snapshot):
            raise TypeError('Unsupported Snapshot class')
        return ss


@Reader.register_driver('protobuf')
class DriverProtobuf:
    """Protobuf format reader

    A Driver for the :class:`Reader` class which supports the protobuf format gzipped.

    Args:
        path (:obj:`str`): Path to the gzip file
    """
    def __init__(self, path):
        self.fd = gzip.open(path, 'rb')
        self.msg_size_format = '<L'
        self.msg_size_length = struct.calcsize(self.msg_size_format)
        self.gender_enum = {0: 'm', 1: 'f', 2: 'o'}

    def __del__(self):
        self.fd.close()

    def _read(self, n):
        data = self.fd.read(n)
        if data:
            return data
        else:
            raise EOFError()

    def read_user(self):
        """Reads user information from the file

        Returns:
            protocol_user (:class:`cortex.net.protocol.User`)
        """
        msg_size, = struct.unpack(self.msg_size_format, self._read(self.msg_size_length))
        user = cortex_pb2.User()
        user.ParseFromString(self._read(msg_size))

        birthday = datetime.utcfromtimestamp(user.birthday)\
            .replace(tzinfo=pytz.utc)\
            .astimezone(_LOCAL_TZ)\
            .replace(tzinfo=None)
        protocol_user = protocol.User(uid=user.user_id,
                                      name=user.username,
                                      birthday=birthday,
                                      gender=self.gender_enum[user.gender])
        return protocol_user

    def read_snapshot(self):
        """Reads a single snapshot from the file

        Returns:
            protocol_snapshot (:class:`cortex.net.protocol.Snapshot`)
        """
        msg_size, = struct.unpack(self.msg_size_format, self._read(self.msg_size_length))
        snapshot = cortex_pb2.Snapshot()
        snapshot.ParseFromString(self._read(msg_size))

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

        timestamp_ms = datetime.utcfromtimestamp(snapshot.datetime/1000)\
            .replace(tzinfo=pytz.utc)\
            .astimezone(_LOCAL_TZ)\
            .replace(tzinfo=None)
        protocol_snapshot = protocol.Snapshot(timestamp_ms,
                                              pose,
                                              image_color,
                                              image_depth,
                                              feelings)
        return protocol_snapshot


