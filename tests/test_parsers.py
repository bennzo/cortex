import pytest
import subprocess
import datetime
import bson
from cortex.parsers import run_parser


_SNAPSHOT_RAW = "data/snapshot.raw"
_USER = {'user': {'uid': 42, 'name': 'Dan Gittik', 'birthday': datetime.datetime(1992, 3, 5, 0, 0), 'gender': 'm'}}
_POSE = {'snapshot': {'timestamp_ms': datetime.datetime(2019, 12, 4, 10, 8, 7, 339000),
                      'pose': {'translation': [0.4873843491077423,
                                               0.007090016733855009,
                                               -1.1306129693984985],
                               'rotation': [-0.10888676356214629,
                                            -0.26755994585035286,
                                            -0.021271118915446748,
                                            0.9571326384559261]}}}
_IMAGE_COLOR = {'snapshot': {'timestamp_ms': datetime.datetime(2019, 12, 4, 10, 8, 7, 339000),
                             'image_color': {'image_color': 'data/temp/42/2019-12-04_10-08-07-339000/image_color.tiff',
                                             'width': 1920, 'height': 1080}}}
_IMAGE_DEPTH = {'snapshot': {'timestamp_ms': datetime.datetime(2019, 12, 4, 10, 8, 7, 339000),
                             'image_depth': {'image_depth': 'data/temp/42/2019-12-04_10-08-07-339000/image_depth.tiff',
                                             'width': 172, 'height': 224}}}
_FEELINGS = {'snapshot': {'timestamp_ms': datetime.datetime(2019, 12, 4, 10, 8, 7, 339000),
                          'feelings': {'hunger': 0.0, 'thirst': 0.0, 'exhaustion': 0.0, 'happiness': 0.0}}}


@pytest.mark.parametrize('field, result', [
    ('pose', {**_USER, **_POSE}),
    ('image_color', {**_USER, **_IMAGE_COLOR}),
    ('image_depth', {**_USER, **_IMAGE_DEPTH}),
    ('feelings', {**_USER, **_FEELINGS})
])
def test_run_parser(field, result):
    enc_result = bson.encode(result)
    with open(_SNAPSHOT_RAW, 'rb') as f:
        raw_data = f.read()
    assert run_parser(field, raw_data) == enc_result


@pytest.mark.parametrize('field, result', [
    ('pose', {**_USER, **_POSE}),
    ('image_color', {**_USER, **_IMAGE_COLOR}),
    ('image_depth', {**_USER, **_IMAGE_DEPTH}),
    ('feelings', {**_USER, **_FEELINGS})
])
def test_parse(field, result, tmp_path):
    enc_result = bson.encode(result)
    tmp_file = tmp_path / f'{field}.raw'
    with open(tmp_file, 'wb+') as fd:
        subprocess.run(["python",
                        "-m",
                        "cortex.parsers",
                        "parse", field, _SNAPSHOT_RAW], stdout=fd)
    assert tmp_file.read_bytes() == enc_result
