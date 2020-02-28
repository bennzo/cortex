import json

parsers = {}


def parser(field):
    def decorator(f):
        parsers[field] = f
        return f
    return decorator


def parse(field, directory, data):
    parsers[field](directory, data)


@parser('translation')
def parse_translation(directory, xyz):
    with open(directory / 'translation.json', 'w+') as writer:
        json.dump(dict(zip('xyz', xyz)), writer)


@parser('image_color')
def parse_image_color(directory, image_color):
    image_color.save(directory / 'image_color.jpg')



