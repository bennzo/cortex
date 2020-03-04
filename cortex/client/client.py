import requests
from . import reader
from ..net import protocol, Connection

HEADER_FORMAT = '<QQL'


class Client:
    def __init__(self, host, port, sample, format):
        self.host = host
        self.port = port
        self.reader = reader.Reader(sample, format)

    def run(self):
        for snapshot in self.reader:
            with Connection.connect(self.host, self.port) as conn:
                conn.send(self.hello.serialize())
                config = protocol.Config.deserialize(conn.receive())
                supported_ss = protocol.Snapshot(snapshot['datetime'].timestamp(),
                                                 **{f: snapshot[f] for f in config.fields})
                conn.send(supported_ss.serialize())


def upload_sample(host, port, path, sample_format='protobuf'):
    try:
        client = Client(host, port, path, sample_format)
        client.run()
    except IOError as e:
        print(f'ERROR: {e}')
        return 1
