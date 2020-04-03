import pytest
import datetime
import pymongo
import mongomock

from cortex.saver import Saver

_DB_URL = 'mongodb://127.0.0.1:27017'
_RESULTS = ['pose', 'image_color', 'image_depth', 'feelings']
_STORED_USER = {'uid': 42, 'name': 'Dan Gittik', 'birthday': datetime.datetime(1992, 3, 5, 0, 0), 'gender': 'm', 'snapshots': [{'timestamp_ms': datetime.datetime(2019, 12, 4, 10, 8, 7, 339000), 'pose': {'translation': [0.4873843491077423, 0.007090016733855009, -1.1306129693984985], 'rotation': [-0.10888676356214629, -0.26755994585035286, -0.021271118915446748, 0.9571326384559261]}, 'image_color': {'image_color': 'data/temp/42/2019-12-04_10-08-07-339000/image_color.tiff', 'width': 1920, 'height': 1080}, 'image_depth': {'image_depth': 'data/temp/42/2019-12-04_10-08-07-339000/image_depth.tiff', 'width': 172, 'height': 224}, 'feelings': {'hunger': 0.0, 'thirst': 0.0, 'exhaustion': 0.0, 'happiness': 0.0}}]}


@pytest.fixture()
def mock_mongo(monkeypatch):
    monkeypatch.setattr(pymongo, 'MongoClient', mongomock.MongoClient)


def test_saver(mock_mongo):
    saver = Saver(_DB_URL)
    for field in _RESULTS:
        with open(f'data/{field}.result', 'rb') as fd:
            data = fd.read()
            saver.save(field, data)

    stored_user = saver.client.users.find_one(filter={'uid': 42},
                                              projection={'_id': False})
    assert stored_user == _STORED_USER

