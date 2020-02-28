import datetime
from ..core import reader, protocol
from ..utils import Connection

HEADER_FORMAT = '<QQL'


class Client:
    def __init__(self, host, port, sample, sample_type):
        self.host = host
        self.port = port
        self.reader = reader.Reader(sample, sample_type)
        self.hello = protocol.Hello(self.reader.user_id,
                                    self.reader.user_name,
                                    self.reader.user_bdate,
                                    self.reader.user_gender)

    def run(self):
        for snapshot in self.reader:
            with Connection.connect(self.host, self.port) as conn:
                conn.send(self.hello.serialize())
                config = protocol.Config.deserialize(conn.receive())
                supported_ss = protocol.Snapshot(snapshot['datetime'].timestamp(),
                                                 **{f: snapshot[f] for f in config.fields})
                conn.send(supported_ss.serialize())


def run_client(host, port, sample):
    try:
        client = Client(host, int(port), sample)
        client.run()
    except IOError as e:
        print(f'ERROR: {e}')
        return 1
