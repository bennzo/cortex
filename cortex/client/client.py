import requests
import bson
from . import reader
from ..net import protocol


class Client:
    """A Simple client that is used to upload snapshots.

    By running the client, it will connect to the server, parse a sample file containing user info
    and snapshots, and finally upload the snapshots to the server.

    Attributes:
        host (str): Hostname of the server
        port (int): Port of the server
        reader (:obj:`cortex.client.reader.Reader`): Sample reader
        user (:obj:`cortex.net.protocol.User`): Protocol User instance (holds the user information)

    Args:
        host (str): Hostname of the server
        port (int): Port of the server
        sample (str): Path to the file containing user information and snapshots
        sample_format (str): Identifier for the sample format.
            Note: Has to be supported by :class:`cortex.client.reader.Reader`
    """
    def __init__(self, host, port, sample, sample_format):
        self.host = host
        self.port = port
        self.reader = reader.Reader(sample, sample_format)
        self.user = self.reader.read_user()

    def run(self):
        """Begins the sample uploading sequence.

        Iterating over the sample and uploading its contained snapshots
        """
        server_config = self._get_config()
        for snapshot in self.reader:
            self._post_snapshot(snapshot, server_config.parsers)

    def _get_config(self):
        response = requests.get(f'http://{self.host}:{self.port}/config')
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = response.data
        if response.status_code == 200:
            config = protocol.Config.from_bson(bson.decode(content))
        else:
            raise ConnectionError(f'Unable to get server configuration:\n'
                                  f'Status:{response.status_code} Message:{response.reason}')
        return config

    def _post_snapshot(self, snapshot, fields):
        response = requests.post(f'http://{self.host}:{self.port}/snapshot',
                                 headers={'Content-Type': 'application/bson'},
                                 data=bson.encode({'user': self.user.to_bson(),
                                                   'snapshot': snapshot.to_bson(fields=fields)}))
        if response.status_code != 200:
            raise ConnectionError(f'Unable to send snapshot to server:\n'
                                  f'Status:{response.status_code} Message:{response.reason}')
        return response.status_code


def upload_sample(host, port, path, sample_format='protobuf'):
    """ Uploads a sample file to the server.

    Args:
        host (str): Hostname of the server
        port (int): Port of the server
        path (str): Path to the file containing user information and snapshots
        sample_format (str, optional): Identifier for the sample format.
            Note: Has to be supported by :class:`cortex.client.reader.Reader`

    Returns:
        1 if an IOError as occurred, 0 otherwise.
    """
    try:
        client = Client(host, port, path, sample_format)
        client.run()
    except IOError as e:
        print(f'ERROR: {e}')
        return 1
    return 0
