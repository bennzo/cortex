import struct
import PIL.Image
import PIL.ImageOps
from datetime import datetime


class Reader:
    def __init__(self, path, parser, has_header=True):
        self.fd = open(path, 'rb')
        self.parser = parsers[parser]()
        if has_header:
            header = self.parser.parse_header(self.fd)
            self.__dict__ = {**self.__dict__, **header}

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.parser.parse(self.fd)
        except EOFError:
            raise StopIteration


class ParserBinary:
    def __init__(self):
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

    def parse_header(self, fd):
        header_vals = []
        for i, fmt in enumerate(self.header_fmts):
            header_vals += struct.unpack(fmt, fd.read(struct.calcsize(fmt)))
            if i == 0:
                header_vals += [fd.read(header_vals[-1]).decode()]
        # Convert birth timestamp to datetime
        header_vals[3] = datetime.fromtimestamp(header_vals[3])
        return dict(zip(self.header_names, header_vals))

    def parse(self, fd):
        snap_vals = []
        for i, fmt in enumerate(self.snap_fmts):
            e_snap_vals = fd.read(struct.calcsize(fmt))
            if e_snap_vals == b'':
                raise EOFError
            snap_vals += struct.unpack(fmt, e_snap_vals)
            if i == 0:
                h, w = snap_vals[-2], snap_vals[-1]
                img_bin_bgr = fd.read(3*h*w)
                img_rgb_flip = PIL.Image.frombytes('RGB', (w, h), img_bin_bgr[::-1])
                img_rgb = PIL.ImageOps.flip(PIL.ImageOps.mirror(img_rgb_flip))
                snap_vals += [img_rgb]
            if i == 1:
                h, w = snap_vals[-2], snap_vals[-1]
                img_bin = fd.read(4*h*w)
                snap_vals += [PIL.Image.frombytes('F', (w, h), img_bin)]
        # Convert timestamp to datetime
        snap_vals[0] = datetime.fromtimestamp(snap_vals[0] / 1000)
        snapshot_dict = dict(zip(self.snap_names, snap_vals))
        snapshot_dict['translation'] = (snapshot_dict['loc_x'], snapshot_dict['loc_y'], snapshot_dict['loc_z'])
        return snapshot_dict


parsers = {'binary': ParserBinary}

if __name__ == '__main__':
    reader = Reader('../../data/sample.mind', 'binary')
    for ss in reader:
        pass