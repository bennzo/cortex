import importlib
import bson
from ..utils import parse_url


class Saver:
    def __init__(self, db_url):
        scheme, host, port = parse_url(db_url)
        # Connect to db
        db_module = importlib.import_module(name=f'..net.db.{scheme}',
                                            package='cortex.saver')
        client = db_module.SaverClient(host, port)

    def __del__(self):
        pass

    def save(self, field, data):
        data = bson.decode(data)
        # save to db
        pass


def _cli_save(db_url, field, data_path):
    saver = Saver(db_url)
    with open(data_path) as fd:
        raw_data = fd.read()
        saver.save(field, raw_data)


def _cli_run_saver(db_url, mq_url):
    saver = Saver(db_url)

    # Import message queue module
    mq_scheme, mq_host, mq_port = parse_url(mq_url)
    mq_module = importlib.import_module(name=f'..net.mq.{mq_scheme}',
                                        package='cortex.server')
    mq_client = mq_module.SaverClient(mq_host, mq_port, saver)
    mq_client.consume()
