import struct
import gzip
import PIL.Image
import PIL.ImageOps
from datetime import datetime
import cortex_pb2


class Reader:
    drivers = {}
    msgsize_type = '<L'

    def __init__(self, path, serialize_type):
        self.driver = Reader.drivers[serialize_type](path)
        self.user = self.driver.read_user()
            # self.__dict__ = {**self.__dict__, **header}

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.driver.read_snapshot()
        except EOFError:
            raise StopIteration

    @staticmethod
    def register_driver(name):
        def decorator(c):
            Reader.drivers[name] = c
            return c
        return decorator


@Reader.register_driver('protobuf')
class DriverProtobuf:
    def __init__(self, path):
        self.fd = gzip.open(path, 'rb')
        self.msg_size_format = '<L'
        self.msg_size_length = struct.calcsize(self.msg_size_format)

    def __del__(self):
        self.fd.close()

    def read_user(self):
        msg_size, = struct.unpack(self.msg_size_format, self.fd.read(self.msg_size_length))
        user = cortex_pb2.User()
        user.ParseFromString(self.fd.read(msg_size))
        return user

    def read_snapshot(self):
        msg_size, = struct.unpack(self.msg_size_format, self.fd.read(self.msg_size_length))
        snapshot = cortex_pb2.Snapshot()
        snapshot.ParseFromString(self.fd.read(msg_size))
        return snapshot


@Reader.register_driver('binary')
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
    reader = Reader('../../data/sample.mind.gz', 'protobuf')
    for ss in reader:
        pass