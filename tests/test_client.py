import pytest
import datetime
import requests
import bson
from cortex.client import Client, upload_sample
from cortex.client.reader import Reader
from cortex.net.protocol import Snapshot, Config

_HOST = '127.0.0.1'
_PORT = 8000
_SAMPLE = 'data/littlesample.mind.gz'
_SAMPLE_FORMAT = 'protobuf'


@pytest.fixture
def mock_response(monkeypatch):
    def mock_get(url):
        return MockGetResponse()

    def mock_post(url, headers, data):
        return MockPostResponse()

    monkeypatch.setattr(requests, 'get', mock_get)
    monkeypatch.setattr(requests, 'post', mock_post)


class MockGetResponse:
    data = bson.encode({'parsers': ['pose', 'image_color', 'image_depth', 'feelings']})
    status_code = 200


class MockPostResponse:
    status_code = 200


@pytest.fixture
def client():
    return Client(host=_HOST, port=_PORT, sample=_SAMPLE, sample_format=_SAMPLE_FORMAT)


@pytest.fixture
def reader():
    return Reader(path=_SAMPLE, driver_type=_SAMPLE_FORMAT)


def test_reader(reader):
    user = reader.read_user()
    assert user.uid == 42
    assert user.name == 'Dan Gittik'
    assert user.birthday == datetime.datetime(1992, 3, 5, 0, 0)
    assert user.gender == 'm'

    snapshot = reader.read_snapshot()
    snapshot_dict = snapshot.to_bson()
    assert snapshot_dict['timestamp_ms'] == datetime.datetime(2019, 12, 4, 10, 8, 7, 339000)
    assert snapshot_dict['pose']['translation'] == (0.4873843491077423, 0.007090016733855009, -1.1306129693984985)
    assert snapshot_dict['pose']['rotation'] == (-0.10888676356214629, -0.26755994585035286, -0.021271118915446748, 0.9571326384559261)
    assert snapshot_dict['image_color']['width'] == 1920
    assert snapshot_dict['image_color']['height'] == 1080
    assert snapshot_dict['image_depth']['width'] == 172
    assert snapshot_dict['image_depth']['height'] == 224
    assert snapshot_dict['feelings']['hunger'] == 0.0
    assert snapshot_dict['feelings']['thirst'] == 0.0
    assert snapshot_dict['feelings']['exhaustion'] == 0.0
    assert snapshot_dict['feelings']['happiness'] == 0.0

    snapshot2 = reader.read_snapshot()
    assert isinstance(snapshot2, Snapshot)


def test_get_config(client, mock_response):
    config = client._get_config()
    assert isinstance(config, Config)
    assert config.parsers == ['pose', 'image_color', 'image_depth', 'feelings']


def test_post_snapshot(client, mock_response):
    config = ['pose', 'image_color', 'image_depth', 'feelings']
    snapshot = client.reader.read_snapshot()
    statuscode = client._post_snapshot(snapshot=snapshot, fields=config)
    assert statuscode == 200


def test_upload_sample(mock_response):
    assert upload_sample(host=_HOST, port=_PORT, path=_SAMPLE) == 0


