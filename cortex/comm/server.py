import threading
import struct
from pathlib import Path
from datetime import datetime
from ..utils import Listener, parser
from ..core import protocol

HEADER_FORMAT = '<QQL'


class Session(threading.Thread):
    _recv_lock = threading.Lock()
    _mem_lock = threading.Lock()
    # _write_locks = {}

    def __init__(self, connection, data_dir, config):
        super().__init__()
        self.conn = connection
        self.dir = data_dir
        self.server_config = config

    def run(self):
        hello = protocol.Hello.deserialize(self.conn.receive())
        self.conn.send(protocol.Config(self.server_config).serialize())
        snapshot = protocol.Snapshot.deserialize(self.conn.receive())
        self.store_ss(hello, snapshot)

    def store_ss(self, hello, snapshot):
        uid = str(hello.user_id)
        date = datetime.fromtimestamp(snapshot.ts).strftime('%Y-%m-%d_%H-%M-%S-%f')
        user_dir = self.dir / uid / date
        user_dir.mkdir(parents=True, exist_ok=True)
        for field in self.server_config:
            parser.parse(field, user_dir, snapshot.__dict__[field])


class Server:
    config = ['translation',
              'image_color']

    def __init__(self, host, port, data):
        self.data_dir = Path(data)
        self.listener = Listener(int(port), host=host)

    def __call__(self):
        self.listener.start()
        try:
            while True:
                try:
                    conn = self.listener.accept()
                    tr = Session(conn, self.data_dir, Server.config)
                    tr.start()
                except KeyboardInterrupt:
                    break
        except Exception as e:
            print(f'ERROR: {e}')
            return 1
        finally:
            self.listener.stop()
        return 0


def run_server(host, port, data):
    server = Server(host, int(port), data)
    return server()
