import bson
from PIL import Image


class User:
    def __init__(self, uid, name, birthday, gender):
        self.uid = uid
        self.name = name
        self.birthday = birthday
        self.gender = gender

    def serialize(self):
        user_doc = {'uid': self.uid,
                    'name': self.name,
                    'birthday': self.birthday,
                    'gender': self.gender}
        return bson.encode(user_doc)

    @staticmethod
    def deserialize(data):
        bson_repr = bson.decode(data)
        return User(**bson_repr)


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
    def __init__(self, translation=(0, 0, 0), rotation=(0, 0, 0, 0)):
        self.translation = translation
        self.rotation = rotation

    def serialize(self):
        pose_doc = {'translation': self.translation, 'rotation': self.rotation}
        return bson.encode(pose_doc)

    @staticmethod
    def deserialize(data):
        pose_doc = bson.decode(data)
        return Pose(**pose_doc)


@Snapshot.field('image_color')
class ImageColor:
    def __init__(self, image_color=None):
        self.image_color = image_color
        self.height, self.width = image_color.shape

    def serialize(self):
        image_doc = {'image_color': b'' if self.image_color is None else self.image_color.tobytes(),
                     'width': self.width,
                     'height': self.height}
        return bson.encode(image_doc)

    @staticmethod
    def deserialize(data):
        image_doc = bson.decode(data)
        image_bytes, w, h = image_doc['image_color'], image_doc['width'], image_doc['height']
        image_color = None if len(image_bytes) == 0 else Image.frombytes('RGB', (w, h), image_bytes)
        return ImageColor(image_color)


@Snapshot.field('image_depth')
class ImageDepth:
    def __init__(self, image_depth=None):
        self.image_depth = image_depth
        self.height, self.width = image_depth.shape

    def serialize(self):
        image_doc = {'image_depth': b'' if self.image_depth is None else self.image_depth.tobytes(),
                     'width': self.width,
                     'height': self.height}
        return bson.encode(image_doc)

    @staticmethod
    def deserialize(data):
        image_doc = bson.decode(data)
        image_bytes, w, h = image_doc['image_depth'], image_doc['width'], image_doc['height']
        image_depth = None if len(image_bytes) == 0 else Image.frombytes('F', (w, h), image_bytes)
        return ImageColor(image_depth)


@Snapshot.field('feelings')
class Feelings:
    def __init__(self, hunger, thirst, exhaustion, happiness):
        self.hunger = hunger
        self.thirst = thirst
        self.exhaustion = exhaustion
        self.happiness = happiness

    def serialize(self):
        feelings_doc = {'hunger': self.hunger,
                        'thirst': self.thirst,
                        'exhaustion': self.exhaustion,
                        'happiness': self.happiness}
        return bson.encode(feelings_doc)

    @staticmethod
    def deserialize(data):
        feelings_doc = bson.decode(data)
        return Feelings(**feelings_doc)



if __name__ == '__main__':
    import time
    test = User(50, 'ben', int(time.time()), 'm')
    test_bson = test.serialize()