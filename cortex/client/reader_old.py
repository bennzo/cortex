import struct
import gzip
from pathlib import Path
from datetime import datetime

import PIL.Image
import PIL.ImageOps

from ..net import protocol
from .utils import cortex_pb2


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
    msgsize_type = '<L'

    def __init__(self, path):
        self.path = Path(path)
        self.driver = Reader.drivers[self.path.suffix](path)
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
        if not isinstance(user, cortex_pb2.User):
            raise TypeError('Unsupported User class')
        return user

    def read_snapshot(self):
        ss = self.driver.read_snapshot()
        if not isinstance(ss, cortex_pb2.Snapshot):
            raise TypeError('Unsupported Snapshot class')
        return ss


@Reader.register_driver('.gz')
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

        pose = protocol.Pose(translation=(snapshot.Pose.Translation.x,
                                          snapshot.Pose.Translation.y,
                                          snapshot.Pose.Translation.z),
                             rotation=(snapshot.Pose.Rotation.x,
                                       snapshot.Pose.Rotation.y,
                                       snapshot.Pose.Rotation.z,
                                       snapshot.Pose.Rotation.w))
        if len(snapshot.ImageColor.data) == 0:
            image_color = None
        else:
            image_color = Image.frombytes('RGB',
                                          (snapshot.ImageColor.width, snapshot.ImageColor.height),
                                          snapshot.ImageColor.data)
        if len(snapshot.ImageDepth.data) == 0:
            image_depth = None
        else:
            image_depth = Image.frombytes('RGB',
                                          (snapshot.ImageDepth.width, snapshot.ImageDepth.height),
                                          snapshot.ImageDepth.data)
        feelings = protocol.Feelings(hunger=snapshot.Feelings.hunger,
                                     thirst=snapshot.Feelings.thirst,
                                     exhaustion=snapshot.Feelings.exhaustion,
                                     happiness=snapshot.Feelings.happiness)
        protocol_snapshot = protocol.Snapshot(datetime.fromtimestamp(snapshot.datetime),
                                              pose,
                                              image_color,
                                              image_depth,
                                              feelings)
        return protocol_snapshot


@Reader.register_driver('')
class DriverBinary:
    def __init__(self, path):
        self.fd = open(path, 'rb')

        self.header_fmts = ['<QL', '<Lc']
        self.header_names = ['user_id',
                             'user_namesize',
                             'user_name',
                             'user_bdate',
                             'user_gender']

        self.snap_fmts = ['<QdddddddLL', '<LL', '<ffff']
        self.snap_names = ['datetime',
                           'loc_x', 'loc_y', 'loc_z',
                           'rot_x', 'rot_y', 'rot_z', 'rot_w',
                           'clr_h', 'clr_w', 'image_color',
                           'dep_h', 'dep_w', 'image_depth',
                           'hunger', 'thirst', 'exhaust', 'happy']

    def read_user(self):
        header_vals = []
        for i, fmt in enumerate(self.header_fmts):
            header_vals += struct.unpack(fmt, self.fd.read(struct.calcsize(fmt)))
            if i == 0:
                header_vals += [self.fd.read(header_vals[-1]).decode()]
        # Convert birth timestamp to datetime
        header_vals[3] = datetime.fromtimestamp(header_vals[3])
        return dict(zip(self.header_names, header_vals))

    def read_snapshot(self):
        snap_vals = []
        for i, fmt in enumerate(self.snap_fmts):
            e_snap_vals = self.fd.read(struct.calcsize(fmt))
            if e_snap_vals == b'':
                raise EOFError
            snap_vals += struct.unpack(fmt, e_snap_vals)
            if i == 0:
                h, w = snap_vals[-2], snap_vals[-1]
                img_bin_bgr = self.fd.read(3*h*w)
                img_rgb_flip = PIL.Image.frombytes('RGB', (w, h), img_bin_bgr[::-1])
                img_rgb = PIL.ImageOps.flip(PIL.ImageOps.mirror(img_rgb_flip))
                snap_vals += [img_rgb]
            if i == 1:
                h, w = snap_vals[-2], snap_vals[-1]
                img_bin = self.fd.read(4*h*w)
                snap_vals += [PIL.Image.frombytes('F', (w, h), img_bin)]
        # Convert timestamp to datetime
        snap_vals[0] = datetime.fromtimestamp(snap_vals[0] / 1000)
        snapshot_dict = dict(zip(self.snap_names, snap_vals))
        snapshot_dict['translation'] = (snapshot_dict['loc_x'], snapshot_dict['loc_y'], snapshot_dict['loc_z'])
        return snapshot_dict


if __name__ == '__main__':
    reader = Reader('../../data/sample.mind.gz')
    for ss in reader:
        pass