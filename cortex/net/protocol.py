import bson
from PIL import Image

"""
This module encompasses the protocol used for communication between the Server and the Client.
Basically, each class in this module represents a message which can be encoded/decoded by the BSON format.
"""


class User:
    """User message

    Contains information about the client user.

    Args:
        uid (int): User ID
        name (str): Username
        birthday (datetime): Date of birth
        gender (char): Gender identifier (m/f)
    """
    def __init__(self, uid, name, birthday, gender):
        self.uid = uid
        self.name = name
        self.birthday = birthday
        self.gender = gender

    def to_bson(self):
        """Encodes the user message into a dictionary

        Returns:
            dict: User message dictionary
        """
        user_doc = {'uid': self.uid,
                    'name': self.name,
                    'birthday': self.birthday,
                    'gender': self.gender}
        return user_doc

    @staticmethod
    def from_bson(data):
        """Decodes a user dictionary into a :class:`User` instance

        Args:
            data (dict): BSON Dictionary containing user information
        Returns:
            :class:`User`: User instance
        """
        return User(**data)


class Config:
    """Config message

    Contains information about the server configuration, more specifically, which snapshot fields the server
    is able to parse.

    Args:
        parsers (list[str]): List of parser names.
    """
    def __init__(self, parsers):
        self.parsers = parsers

    def to_bson(self):
        """Encodes the config message into a dictionary

        Returns:
            dict: Config message dictionary
        """
        config_doc = {'parsers': self.parsers}
        return config_doc

    @staticmethod
    def from_bson(data):
        """Decodes a config dictionary into a :class:`Config` instance

        Args:
            data (dict): BSON Dictionary containing config information
        Returns:
            :class:`Config`: Config instance
        """
        return Config(**data)


class Snapshot:
    """Snapshot message

    Contains information about a snapshot, each attribute is a sub-message containing information about a
    different field.

    Note:
        In order to add new fields (sub-message) to the snapshot a new class has to be implemented and match
        the following requirements:
            Registration
                - Decorated by :meth:`Snapshot.field` initialized with the appropriate field name.
            Interface
                - to_bson(): Encode the sub-message information into a BSON dictionary
                - from_bson(data): Decode a BSON dictionary into the sub-message class
            See :class:`Pose` for example.

    Args:
         timestamp_ms (:obj:`datetime.datetime`): Timestamp of the snapshot
         pose (:class:`Pose`): Pose sub-message
         image_color (:class:`ImageColor`): ImageColor sub-message
         image_depth (:class:`ImageDepth`): ImageDepth sub-message
         feelings (:class:`Feelings`): Feelings sub-message
    """
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
        """Encodes the config message into a dictionary

        Returns:
            dict: Config message dictionary
        """
        fields = fields or Snapshot.fields
        snapshot_doc = {'timestamp_ms': self.timestamp_ms}
        for fname in fields:
            fval = getattr(self, fname)
            if fval is not None:
                snapshot_doc[fname] = fval.to_bson()
        return snapshot_doc

    @staticmethod
    def from_bson(data):
        """Decodes a config dictionary into a :class:`Config` instance

        Args:
            data (dict): BSON Dictionary containing config information
        Returns:
            :class:`Config`: Config instance
        """
        snapshot_doc = data
        for fname, fclass in Snapshot.fields.items():
            if fname not in snapshot_doc:
                continue
            try:
                snapshot_doc[fname] = fclass.from_bson(snapshot_doc[fname])
            except Exception as e:
                print(f'Error decoding field - <{fname}>:')
                print(e)
        return Snapshot(**snapshot_doc)

    @staticmethod
    def from_bson_partial(data):
        snapshot_doc = bson.decode(data)
        return Snapshot(**snapshot_doc)

    @staticmethod
    def field(name):
        """A Decorator for registering new snapshot sub-messages.

        Args:
            name (:obj:`str`): The name of the registered sub-message
        """
        def decorator(field_class):
            Snapshot.fields[name] = field_class
            return field_class
        return decorator


@Snapshot.field('pose')
class Pose:
    """Pose sub-message

    Contains information about the pose of the snapshot

    Args:
        translation (:obj:`tuple`): A Triplet <x,y,z> of floats depicting the translation of pose
        translation (:obj:`tuple`): A Quartet <x,y,z,w> of floats depicting the rotation of pose
    """
    def __init__(self, translation=(0, 0, 0), rotation=(0, 0, 0, 0)):
        self.translation = translation
        self.rotation = rotation

    def to_bson(self):
        """Encodes the Pose sub-message into a dictionary

        Returns:
            dict: Pose sub-message dictionary
        """
        pose_doc = {'translation': self.translation, 'rotation': self.rotation}
        return pose_doc

    @staticmethod
    def from_bson(data):
        """Decodes a Pose dictionary into a :class:`Pose` instance

        Args:
            data (dict): BSON Dictionary containing Pose information
        Returns:
            :class:`Pose`: Pose instance
        """
        pose_doc = data
        return Pose(**pose_doc)


@Snapshot.field('image_color')
class ImageColor:
    """ImageColor sub-message

    Contains information about the ImageColor of the snapshot

    Args:
        image_color (:obj:`numpy.ndarray`): RGB Image represented as a 3d numpy array
        width (:obj:`int`): Width of image_color
        height (:obj:`int`): Height of image_color
    """
    def __init__(self, image_color=None):
        self.image_color = image_color
        self.width, self.height = (0, 0) if image_color is None else image_color.size

    def to_bson(self):
        """Encodes the ImageColor sub-message into a dictionary

        Returns:
            dict: ImageColor sub-message dictionary
        """
        image_doc = {'image_color': b'' if self.image_color is None else self.image_color.tobytes(),
                     'width': self.width,
                     'height': self.height}
        return image_doc

    @staticmethod
    def from_bson(data):
        """Decodes a ImageColor dictionary into a :class:`ImageColor` instance

        Args:
            data (dict): BSON Dictionary containing ImageColor information
        Returns:
            :class:`ImageColor`: ImageColor instance
        """
        image_doc = data
        image_bytes, w, h = image_doc['image_color'], image_doc['width'], image_doc['height']
        image_color = None if len(image_bytes) == 0 else Image.frombytes('RGB', (w, h), image_bytes)
        return ImageColor(image_color)


@Snapshot.field('image_depth')
class ImageDepth:
    """ImageDepth sub-message

    Contains information about the ImageDepth of the snapshot

    Args:
        image_depth (:obj:`numpy.ndarray`): Image represented as a 1d float numpy array
        width (:obj:`int`): Width of image_depth
        height (:obj:`int`): Height of image_depth
    """
    def __init__(self, image_depth=None):
        self.image_depth = image_depth
        self.width, self.height = (0, 0) if image_depth is None else image_depth.size

    def to_bson(self):
        """Encodes the ImageDepth sub-message into a dictionary

        Returns:
            dict: ImageDepth sub-message dictionary
        """
        image_doc = {'image_depth': b'' if self.image_depth is None else self.image_depth.tobytes(),
                     'width': self.width,
                     'height': self.height}
        return image_doc

    @staticmethod
    def from_bson(data):
        """Decodes a ImageDepth dictionary into a :class:`ImageDepth` instance

        Args:
            data (dict): BSON Dictionary containing ImageDepth information
        Returns:
            :class:`ImageDepth`: ImageDepth instance
        """
        image_doc = data
        image_bytes, w, h = image_doc['image_depth'], image_doc['width'], image_doc['height']
        image_depth = None if len(image_bytes) == 0 else Image.frombytes('F', (w, h), image_bytes)
        return ImageColor(image_depth)


@Snapshot.field('feelings')
class Feelings:
    """Feelings sub-message

    Contains information about the Feelings of the snapshot

    Args:
        hunger (:obj:`float`): Hunger value
        thirst (:obj:`float`): Thirst value
        exhaustion (:obj:`float`): Exhaustion value
        happiness (:obj:`float`): Happiness value
    """
    def __init__(self, hunger=0, thirst=0, exhaustion=0, happiness=0):
        self.hunger = hunger
        self.thirst = thirst
        self.exhaustion = exhaustion
        self.happiness = happiness

    def to_bson(self):
        """Encodes the Feelings sub-message into a dictionary

        Returns:
            dict: Feelings sub-message dictionary
        """
        feelings_doc = {'hunger': self.hunger,
                        'thirst': self.thirst,
                        'exhaustion': self.exhaustion,
                        'happiness': self.happiness}
        return feelings_doc

    @staticmethod
    def from_bson(data):
        """Decodes a Feelings dictionary into a :class:`Feelings` instance

        Args:
            data (dict): BSON Dictionary containing Feelings information
        Returns:
            :class:`Feelings`: Feelings instance
        """
        feelings_doc = data
        return Feelings(**feelings_doc)
