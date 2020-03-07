import json
from ..utils import parse_url

_PARSERS = {}


def parser(field):
    def decorator(f):
        _PARSERS[field] = f
        return f
    return decorator


@parser('pose')
def parse_translation(directory, xyz):
    with open(directory / 'translation.json', 'w+') as writer:
        json.dump(dict(zip('xyz', xyz)), writer)


@parser('image_color')
def parse_image_color(directory, image_color):
    image_color.save(directory / 'image_color.jpg')


@parser('image_depth')
def parse_image_color(directory, image_color):
    image_color.save(directory / 'image_color.jpg')


@parser('feelings')
def parse_translation(directory, xyz):
    with open(directory / 'translation.json', 'w+') as writer:
        json.dump(dict(zip('xyz', xyz)), writer)


def run_parser(field, data_path):
    pass


def setup_parser(field, message_queue):
    pass
