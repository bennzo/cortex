import struct
import datetime
import bson.BSON
from PIL import Image


class User:
    fmt_uid = '<Q'
    fmt_namesize = '<L'
    fmt_birthday = '<L'
    fmt_gender = '<c'

    def __init__(self, uid, name, birthday, gender):
        self.uid = uid
        self.name = name
        self.birthday = birthday
        self.gender = gender

    def serialize(self):
        bson_repr = {'uid': self.uid,
                     'name': self.name,
                     'birthday': self.birthday,
                     'gender': self.gender}
        return bson.BSON.encode(bson_repr)

    @staticmethod
    def deserialize(data):
        bson_repr = bson.decode_document(data)
        return User(**bson_repr)

    def serialize2(self):
        ename = self.name.encode()
        ebd = int(self.birthday.timestamp())
        msg = b''.join([struct.pack(User.fmt_uid, self.uid),
                        struct.pack(User.fmt_namesize, len(ename)),
                        ename,
                        struct.pack(User.fmt_birthday, ebd),
                        struct.pack(User.fmt_gender, self.gender)])
        return msg

    @staticmethod
    def deserialize2(data):
        l, r = 0, struct.calcsize(User.fmt_uid)
        uid = struct.unpack(User.fmt_uid, data[l:r])

        l, r = r, r+struct.calcsize(User.fmt_namesize)
        namesize = struct.unpack(User.fmt_namesize, data[l:r])

        l, r = r, r+namesize
        name = data[l:r].decode()

        l, r = r, r+struct.calcsize(User.fmt_birthday)
        birthday = struct.unpack(User.fmt_birthday, data[l:r])
        birthday = datetime.datetime.fromtimestamp(birthday)

        l, r = r, r+struct.calcsize(User.fmt_gender)
        gender = struct.unpack(User.fmt_gender, data[l:r]).decode()
        return User(uid, name, birthday, gender)


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

if __name__ == '__main__':
    import time
    test = User(50, 'ben', int(time.time()), 'm')
    test_bson = test.serialize()