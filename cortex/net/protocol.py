import struct
import datetime
import bson
from PIL import Image
from .utils import cortex_pb2


class User:
    def __init__(self, uid, name, birthday, gender):
        self.uid = uid
        self.name = name
        self.birthday = birthday
        self.gender = gender

    @staticmethod
    def deserialize(data):
        bson_repr = bson.decode(data)
        return User(**bson_repr)

    def serialize(self):
        user_doc = {'uid': self.uid,
                    'name': self.name,
                    'birthday': self.birthday,
                    'gender': self.gender}
        return bson.encode(user_doc)


class Config:
    def __init__(self, parsers):
        self.parsers = parsers

    def serialize(self):
        config_doc = {'parsers': self.parsers}
        return bson.encode(config_doc)

    @staticmethod
    def deserialize(data):
        bson_repr = bson.decode(data)
        return Config(**bson_repr)


class Snapshot:
    fields = []

    def __init__(self,
                 timestamp_ms,
                 pose=None,
                 image_color=None,
                 image_depth=None,
                 feelings=None):
        self.timestamp = timestamp_ms
        self.pose = pose
        self.image_color = image_color
        self.image_depth = image_depth
        self.feelings = feelings

    def serialize(self, fields=None):
        snapshot_doc = {'timestamp': self.timestamp}
        for field in fields or Snapshot.fields:
            snapshot_doc[field] = getattr(self, field).serialize()
        return bson.encode(snapshot_doc)

    @staticmethod
    def deserialize(data):
        snapshot_doc = bson.decode(data)
        for field in snapshot_doc.keys():
            snapshot_doc[field] = snapshot_doc.deserialize(snapshot_doc[field])
        return Snapshot(**snapshot_doc)

    @staticmethod
    def deserialize_partial(data):
        snapshot_doc = bson.decode(data)
        return Snapshot(**snapshot_doc)

    @staticmethod
    def field(name):
        def decorator(field_class):
            Snapshot.fields.append(name)
            return field_class
        return decorator

@Snapshot.field('pose')
class Pose:
    def __init__(self, translation=(0,0,0), rotation=(0,0,0,0)):
        pass

@Snapshot.field('image_color')
class ImageColor:
    def __init__(self, image=None):
        pass

@Snapshot.field('image_depth')
class ImageDepth:
    def __init__(self, image=None):
        pass

@Snapshot.field('feelings')
class Feelings:
    def __init__(self, feelings=(0,0,0,0)):
        pass


if __name__ == '__main__':
    import time
    test = User(50, 'ben', int(time.time()), 'm')
    test_bson = test.serialize()