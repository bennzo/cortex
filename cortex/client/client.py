import requests
import bson
from . import reader
from ..net import protocol

_CONFIG = {'sample_format': 'protobuf'}


class Client:
    def __init__(self, host, port, sample, sample_format):
        self.host = host
        self.port = port
        self.reader = reader.Reader(sample, sample_format)
        self.user = self.reader.user

    def run(self):
        server_config = self._get_config()
        for snapshot in self.reader:
            self._post_snapshot(snapshot, server_config.parsers)

    def _get_config(self):
        response = requests.get(f'http://{self.host}:{self.port}/config')
        if response.status_code == 200:
            config = protocol.Config.deserialize(response.content)
        else:
            raise ConnectionError(f'Unable to get server configuration:\n'
                                  f'Status:{response.status_code} Message:{response.reason}')
        return config

    def _post_snapshot(self, snapshot, fields):
        response = requests.post(f'http://{self.host}:{self.port}/snapshot',
                                 headers={'Content-Type': 'application/bson'},
                                 data=bson.encode({'user': self.user.serialize(),
                                                   'snapshot': snapshot.serialize(fields=fields)}))
        if response.status_code != 200:
            raise ConnectionError(f'Unable to send snapshot to server:\n'
                                  f'Status:{response.status_code} Message:{response.reason}')


def upload_sample(host, port, path):
    try:
        client = Client(host, port, path, _CONFIG['sample_format'])
        client.run()
    except IOError as e:
        print(f'ERROR: {e}')
        return 1
