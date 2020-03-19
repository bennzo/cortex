import bson
from PIL import Image


class User:
    def __init__(self, uid, name, birthday, gender):
        self.uid = uid
        self.name = name
        self.birthday = birthday
        self.gender = gender

    def to_bson(self):
        user_doc = {'uid': self.uid,
                    'name': self.name,
                    'birthday': self.birthday,
                    'gender': self.gender}
        return user_doc

    @staticmethod
    def from_bson(data):
        return User(**data)


class Config:
    def __init__(self, parsers):
        self.parsers = parsers

    def to_bson(self):
        config_doc = {'parsers': self.parsers}
        return config_doc

    @staticmethod
    def from_bson(data):
        return Config(**data)


class Snapshot:
    fields = {}

    def __init__(self,
                 timestamp_ms,
                 pose=None,
                 image_color=None,
                 image_depth=None,
                 feelings=None):
        self.timestamp_ms = timestamp_ms
        self.pose = pose
        self.image_color = image_color
        self.image_depth = image_depth
        self.feelings = feelings

    def to_bson(self, fields=None):
        fields = fields or Snapshot.fields
        snapshot_doc = {'timestamp_ms': self.timestamp_ms}
        for fname in fields:
            fval = getattr(self, fname)
            if fval is not None:
                snapshot_doc[fname] = fval.to_bson()
        return snapshot_doc

    @staticmethod
    def from_bson(data):
        snapshot_doc = data
        for fname, fclass in Snapshot.fields.items():
            if fname not in snapshot_doc:
                continue
            try:
                snapshot_doc[fname] = fclass.from_bson(snapshot_doc[fname])
            except Exception as e:
                print(f'Error encoding field - <{fname}>:')
                print(e)
        return Snapshot(**snapshot_doc)

    @staticmethod
    def from_bson_partial(data):
        snapshot_doc = bson.decode(data)
        return Snapshot(**snapshot_doc)

    @staticmethod
    def field(name):
        def decorator(field_class):
            Snapshot.fields[name] = field_class
            return field_class
        return decorator


@Snapshot.field('pose')
class Pose:
    def __init__(self, translation=(0, 0, 0), rotation=(0, 0, 0, 0)):
        self.translation = translation
        self.rotation = rotation

    def to_bson(self):
        pose_doc = {'translation': self.translation, 'rotation': self.rotation}
        return pose_doc

    @staticmethod
    def from_bson(data):
        pose_doc = data
        return Pose(**pose_doc)


@Snapshot.field('image_color')
class ImageColor:
    def __init__(self, image_color=None):
        self.image_color = image_color
        self.width, self.height = (0, 0) if image_color is None else image_color.size

    def to_bson(self):
        image_doc = {'image_color': b'' if self.image_color is None else self.image_color.tobytes(),
                     'width': self.width,
                     'height': self.height}
        return image_doc

    @staticmethod
    def from_bson(data):
        image_doc = data
        image_bytes, w, h = image_doc['image_color'], image_doc['width'], image_doc['height']
        image_color = None if len(image_bytes) == 0 else Image.frombytes('RGB', (w, h), image_bytes)
        return ImageColor(image_color)


@Snapshot.field('image_depth')
class ImageDepth:
    def __init__(self, image_depth=None):
        self.image_depth = image_depth
        self.width, self.height = (0, 0) if image_depth is None else image_depth.size

    def to_bson(self):
        image_doc = {'image_depth': b'' if self.image_depth is None else self.image_depth.tobytes(),
                     'width': self.width,
                     'height': self.height}
        return image_doc

    @staticmethod
    def from_bson(data):
        image_doc = data
        image_bytes, w, h = image_doc['image_depth'], image_doc['width'], image_doc['height']
        image_depth = None if len(image_bytes) == 0 else Image.frombytes('F', (w, h), image_bytes)
        return ImageColor(image_depth)


@Snapshot.field('feelings')
class Feelings:
    def __init__(self, hunger=0, thirst=0, exhaustion=0, happiness=0):
        self.hunger = hunger
        self.thirst = thirst
        self.exhaustion = exhaustion
        self.happiness = happiness

    def to_bson(self):
        feelings_doc = {'hunger': self.hunger,
                        'thirst': self.thirst,
                        'exhaustion': self.exhaustion,
                        'happiness': self.happiness}
        return feelings_doc

    @staticmethod
    def from_bson(data):
        feelings_doc = data
        return Feelings(**feelings_doc)
