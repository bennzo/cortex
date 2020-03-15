import importlib
from pathlib import Path
import bson
from PIL import Image
from ..utils import parse_url


# TODO: Add errors incase a snapshot without a field is parsed
class Parser:
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
        def decorator(f):
            Parser._PARSERS[field] = f
            return f
        return decorator


@Parser.register_parser('pose')
def parse_translation(data):
    return data['pose']


@Parser.register_parser('image_color')
def parse_image_color(data):
    data = data['image_color']
    raw_path = Path(data['image_color'])
    w, h = data['width'], data['height']
    if w * h == 0:
        data['image_color'] = ''
    else:
        with raw_path.open(mode='rb') as fd:
            raw_img = fd.read()
            img_path = str(raw_path.parent / raw_path.stem) + '.tiff'
            img = Image.frombytes('RGB', (w, h), raw_img)
            img.save(img_path)
            data['image_color'] = img_path
    return data


@Parser.register_parser('image_depth')
def parse_image_depth(data):
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
    return data['feelings']


def run_parser(field, data):
    parser = Parser(field)
    return parser(data)


def setup_parser(field, message_queue):
    parser = Parser(field)
    scheme, host, port = parse_url(message_queue)
    mq_module = importlib.import_module(name=f'..net.mq.{scheme}',
                                        package='cortex.parser')
    mq_client = mq_module.ParserClient(host, port, parser)
    return mq_client

