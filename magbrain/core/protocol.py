import struct
import datetime
from PIL import Image


class Hello:
    fmt_id_namesz = '<QL'
    fmt_bd_gen = '<Lc'

    def __init__(self, user_id, user_name, user_bd, user_gen):
        self.user_id = user_id
        self.user_name = user_name
        self.user_bd = user_bd
        self.user_gen = user_gen

    def serialize(self):
        e_id = self.user_id
        e_name = self.user_name.encode()
        e_name_sz = len(e_name)
        e_bd = int(self.user_bd.timestamp())
        e_gen = self.user_gen
        msg = b''.join([struct.pack(Hello.fmt_id_namesz, e_id, e_name_sz),
                        e_name,
                        struct.pack(Hello.fmt_bd_gen, e_bd, e_gen)])
        return msg

    @staticmethod
    def deserialize(data):
        l, r = 0, struct.calcsize(Hello.fmt_id_namesz)
        uid, name_sz = struct.unpack(Hello.fmt_id_namesz, data[l:r])

        l, r = r, r+name_sz
        name = data[l:r].decode()

        l, r = r, r+struct.calcsize(Hello.fmt_bd_gen)
        bd, gen = struct.unpack(Hello.fmt_bd_gen, data[l:r])
        bd = datetime.datetime.fromtimestamp(bd)
        gen = gen.decode()
        return Hello(uid, name, bd, gen)


class Config:
    fmt_field_sz = '<L'

    def __init__(self, fields):
        self.fields = fields

    def serialize(self):
        e_fields = [field.encode() for field in self.fields]
        msg = b''.join([struct.pack(Config.fmt_field_sz, len(ef))+ef for ef in e_fields])
        return msg

    @staticmethod
    def deserialize(data):
        e_fields = []
        fmt_len = struct.calcsize(Config.fmt_field_sz)
        l, r = 0, fmt_len
        while l < len(data):
            e_field_sz = struct.unpack(Config.fmt_field_sz, data[l:r])[0]
            l, r = r, r+e_field_sz

            e_fields.append(data[l:r])
            l, r = r, r+fmt_len
        fields = [ef.decode() for ef in e_fields]
        return Config(fields)


class Snapshot:
    fmt_time_loc = '<Qddddddd'
    fmt_clr = '<LL'
    fmt_dep = '<LL'
    fmt_feelings = '<ffff'

    def __init__(self, timestamp_ms,
                 translation=(0, 0, 0),
                 rotation=(0, 0, 0, 0),
                 image_color=None,
                 image_depth=None,
                 feelings=(0, 0, 0, 0)):
        self.ts = int(timestamp_ms)
        self.translation = translation
        self.rotation = rotation
        self.image_color = image_color
        self.image_color_sz = (0, 0) if image_color is None else image_color.size
        self.image_depth = image_depth
        self.image_depth_sz = (0, 0) if image_depth is None else image_depth.size
        self.feelings = feelings

    def serialize(self):
        e_clr_img = b'' if self.image_color is None else self.image_color.tobytes()
        e_dep_img = b'' if self.image_depth is None else self.image_depth.tobytes()
        msg = b''.join([struct.pack(Snapshot.fmt_time_loc, self.ts, *self.translation, *self.rotation),
                        struct.pack(Snapshot.fmt_clr, *self.image_color_sz),
                        e_clr_img,
                        struct.pack(Snapshot.fmt_dep, *self.image_depth_sz),
                        e_dep_img,
                        struct.pack(Snapshot.fmt_feelings, *self.feelings)])
        return msg

    @staticmethod
    def deserialize(data):
        l, r = 0, struct.calcsize(Snapshot.fmt_time_loc)
        ts, *loc_rot = struct.unpack(Snapshot.fmt_time_loc, data[l:r])
        translation, rotation = loc_rot[:3], loc_rot[3:]

        l, r = r, r+struct.calcsize(Snapshot.fmt_clr)
        clr_w, clr_h = struct.unpack(Snapshot.fmt_clr, data[l:r])
        l, r = r, r+3*clr_h*clr_w
        image_color = None if r == l else Image.frombytes('RGB', (clr_w, clr_h), data[l:r])

        l, r = r, r+struct.calcsize(Snapshot.fmt_dep)
        dep_w, dep_h = struct.unpack(Snapshot.fmt_dep, data[l:r])
        l, r = r, r+dep_h*dep_w
        image_depth = None if r == l else Image.frombytes('F', (dep_w, dep_h), data[l:r])

        l, r = r, r+struct.calcsize(Snapshot.fmt_feelings)
        feelings = struct.unpack(Snapshot.fmt_feelings, data[l:r])
        return Snapshot(ts, translation, rotation, image_color, image_depth, feelings)
