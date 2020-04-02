import pytest
import time
import datetime
import requests

from cortex.client import upload_sample
from cortex.server import Server

_HOST = '127.0.0.1'
_PORT = 8000
_SAMPLE = 'data/littlesample.mind.gz'
_SAMPLE_FORMAT = 'protobuf'
_SNAPSHOT_1 = {'user': {'uid': 42, 'name': 'Dan Gittik', 'birthday': datetime.datetime(1992, 3, 5, 0, 0), 'gender': 'm'}, 'snapshot': {'timestamp_ms': datetime.datetime(2019, 12, 4, 10, 8, 7, 339000), 'pose': {'translation': [0.4873843491077423, 0.007090016733855009, -1.1306129693984985], 'rotation': [-0.10888676356214629, -0.26755994585035286, -0.021271118915446748, 0.9571326384559261]}, 'image_color': {'image_color': 'data/temp/42/2019-12-04_10-08-07-339000/image_color.raw', 'width': 1920, 'height': 1080}, 'image_depth': {'image_depth': 'data/temp/42/2019-12-04_10-08-07-339000/image_depth.raw', 'width': 172, 'height': 224}, 'feelings': {'hunger': 0.0, 'thirst': 0.0, 'exhaustion': 0.0, 'happiness': 0.0}}}
_SNAPSHOT_2 = {'user': {'uid': 42, 'name': 'Dan Gittik', 'birthday': datetime.datetime(1992, 3, 5, 0, 0), 'gender': 'm'}, 'snapshot': {'timestamp_ms': datetime.datetime(2019, 12, 4, 10, 8, 7, 412000), 'pose': {'translation': [0.15600797533988953, 0.08133671432733536, -0.49068963527679443], 'rotation': [-0.2959017411322204, -0.16749024140672616, -0.04752900380336424, 0.9392178514199446]}, 'image_color': {'image_color': 'data/temp/42/2019-12-04_10-08-07-412000/image_color.raw', 'width': 1920, 'height': 1080}, 'image_depth': {'image_depth': 'data/temp/42/2019-12-04_10-08-07-412000/image_depth.raw', 'width': 172, 'height': 224}, 'feelings': {'hunger': 0.0010000000474974513, 'thirst': 0.003000000026077032, 'exhaustion': 0.0020000000949949026, 'happiness': 0.0}}}


@pytest.fixture
def server():
    ser = Server(host=_HOST, port=_PORT, publish=print)
    ser.app.config['TESTING'] = True
    with ser.app.test_client() as client:
        yield client


@pytest.fixture
def mock_requests(monkeypatch, server):
    monkeypatch.setattr(requests, 'get', server.get)
    monkeypatch.setattr(requests, 'post', server.post)


def test_publish(server, capsys, mock_requests):
    time.sleep(1)
    upload_sample(host=_HOST, port=_PORT, path=_SAMPLE)
    stdout, stderr = capsys.readouterr()

    assert stderr == ''
    assert str(_SNAPSHOT_1) in stdout
    assert str(_SNAPSHOT_2) in stdout
