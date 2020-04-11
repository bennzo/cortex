import importlib
import bson
from ..utils import parse_url


class Saver:
    """ Saver class, saves data to the configured database

    Initialized by a database url in the format <mq_name>://<host>:<port>.
    The saver client is dynamically imported from the :mod:`cortex.net.db` module and
    has to be implemented in the appropriate sub-module.
    for example: passing 'mongodb://127.0.0.1:27017' as db_url, a SaverClient
    will be imported from :mod:`cortex.net.db.mongodb` and instantiated.

    Args:
        database_url (:obj:`str`): Database URL in the format <db_name>://<host>:<port>
    """
    def __init__(self, database_url):
        scheme, host, port = parse_url(database_url)
        # Connect to db
        db_module = importlib.import_module(name=f'..net.db.{scheme}',
                                            package='cortex.saver')
        self.client = db_module.SaverClient(host, port)

    def save(self, field, data):
        """Saves data (user info, snapshots) to the appropriate field

        Args:
            field (:obj:`str`): Field name the data is related to
            data (:obj:`str`): BSON string of the data
        """
        data = bson.decode(data)
        result = self.client.save(field, data)
        return result


def _cli_save(db_url, field, data_path):
    saver = Saver(db_url)
    with open(data_path, 'rb') as fd:
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
