import threading
import struct
from pathlib import Path
from datetime import datetime
from ..utils import Listener

HEADER_FORMAT = '<QQL'


class ThoughtHandler(threading.Thread):
    _recv_lock = threading.Lock()
    _mem_lock = threading.Lock()
    # _write_locks = {}

    def __init__(self, connection, data_dir):
        super().__init__()
        self.conn = connection
        self.dir = data_dir

    def run(self):
        uid, timestamp, thought = self.recv_thought()
        self.write_thought(uid, timestamp, thought)

    def recv_thought(self):
        with ThoughtHandler._recv_lock:
            header = self.conn.receive(20)
            uid, timestamp, thought_size = struct.unpack(HEADER_FORMAT, header)
            timestamp = datetime.fromtimestamp(timestamp)
            thought = self.conn.receive(thought_size).decode()
        return uid, timestamp, thought

    def write_thought(self, uid, ts, thought):
        dir_path = Path(self.dir) / str(uid)
        file_name = str(ts).replace(' ', '_').replace(':', '-') + '.txt'
        with ThoughtHandler._mem_lock:
            dir_path.mkdir(parents=True, exist_ok=True)
            file_exists = (dir_path / file_name).exists()
            with open(dir_path / file_name, 'a+') as f:
                if file_exists:
                    f.write('\n')
                f.write(thought)


def run_server(address, data):
    host, port = tuple(address.split(':'))
    server = Listener(int(port), host=host)
    server.start()
    try:
        while True:
            try:
                conn = server.accept()
                tr = ThoughtHandler(conn, data)
                tr.start()
            except KeyboardInterrupt:
                break
    except Exception as e:
        print(f'ERROR: {e}')
        return 1
    finally:
        server.stop()
    return 0
