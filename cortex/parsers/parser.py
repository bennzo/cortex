import importlib
from pathlib import Path
import bson
from PIL import Image
from ..utils import parse_url


class Parser:
    """Generic parser class for snapshot parsing.

    Initialized by a snapshot field name. By calling the instance with data, the call will return
    the parsed data coupled with the user information in a dictionary, 'bsonly' encoded.

    Extending the Parsers's parsing capability:\n
    In order for the Parser to support new snapshot fields, a new parsing function needs to be implemented
    and match the following requirements:
        Registration
            - Decorated by :meth:`Parser.register_parser` initialized with the appropriate field name.
        Interface
            - Recieves a :class:`cortex.net.protocol.Snapshot` in a form of dictionary and parses the appropriate field.

    Args:
        field (str): The snapshot field name to be parsed
    """
    _PARSERS = {}

    def __init__(self, field):
        self.field = field
        try:
            self.parser = Parser._PARSERS[self.field]
        except KeyError as e:
            raise KeyError(f'No parser exists for field: {field}', e)

    def __call__(self, data):
        data = bson.decode(data)
        snapshot = data['snapshot']
        parsed_snapshot = {'timestamp_ms': snapshot['timestamp_ms'],
                           self.field: self.parser(snapshot)}
        return bson.encode({'user': data['user'], 'snapshot': parsed_snapshot})

    @staticmethod
    def register_parser(field):
        """A Decorator for registering parser functions.

        Args:
            field (str): The name of the registered parser
        """
        def decorator(f):
            Parser._PARSERS[field] = f
            return f
        return decorator


@Parser.register_parser('pose')
def parse_translation(data):
    """Pose field parser

    Args:
        data (dict): Snapshot dictionary

    Returns:
        Pose information
    """
    return data['pose']


@Parser.register_parser('image_color')
def parse_image_color(data):
    """Color image field parser

    Args:
        data (dict): Snapshot dictionary

    Returns:
        Color image information
    """
    data = data['image_color']
    raw_path = Path(data['image_color'])
    w, h = data['width'], data['height']
    if w * h == 0:
        data['image_color'] = ''
    else:
        with raw_path.open(mode='rb') as fd:
            raw_img = fd.read()
            img_path = str(raw_path.parent / raw_path.stem) + '.png'
            img = Image.frombytes('RGB', (w, h), raw_img)
            img.save(img_path)
            data['image_color'] = img_path
    return data


@Parser.register_parser('image_depth')
def parse_image_depth(data):
    """Depth image field parser

    Args:
        data (dict): Snapshot dictionary

    Returns:
        Depth image information
    """
    data = data['image_depth']
    raw_path = Path(data['image_depth'])
    w, h = data['width'], data['height']
    if w * h == 0:
        data['image_depth'] = ''
    else:
        with raw_path.open(mode='rb') as fd:
            raw_img = fd.read()
            img_path = str(raw_path.parent / raw_path.stem) + '.tiff'
            img = Image.frombytes('F', (w, h), raw_img)
            img.save(img_path)
            data['image_depth'] = img_path
    return data


@Parser.register_parser('feelings')
def parse_feelings(data):
    """Feelings field parser

    Args:
        data (dict): Snapshot dictionary

    Returns:
        Feelings information
    """
    return data['feelings']


def run_parser(field, data):
    """Takes a field name and a snapshot dictionary and returns encoded parsed data

    Args:
        field (str): Field name to parse
        data (dict): Snapshot dictionary

    Returns:
        data_bytes (str): Bson encoded parsed data
    """
    parser = Parser(field)
    data_bytes = parser(data)
    return data_bytes


def setup_parser(field, message_queue):
    """Sets up a message client queue with the 'field' parser as a consumer

    The parser client is dynamically imported from the :mod:`cortex.net.mq` module and
    has to be implemented in the appropriate sub-module.
    for example: passing 'rabbitmq://127.0.0.1:27017' as message_queue, a ParserClient
    will be imported from :mod:`cortex.net.mq.rabbitmq` and instantiated.

    Args:
        field (str): Field name to parse
        message_queue (str): message queue URL in the format <mq_name>://<host>:<port>

    Returns:
        ParserClient
    """
    parser = Parser(field)
    scheme, host, port = parse_url(message_queue)
    mq_module = importlib.import_module(name=f'..net.mq.{scheme}',
                                        package='cortex.parser')
    mq_client = mq_module.ParserClient(host, port, parser)
    return mq_client

