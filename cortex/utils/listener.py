import socket
import inspect
from .connection import Connection


class Listener:
    def __init__(self, port, host='0.0.0.0', backlog=1000, reuseaddr=True):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.reuseaddr = reuseaddr
        self.sock = socket.socket()
        if reuseaddr:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.backlog = backlog

    def __repr__(self):
        cls = type(self).__name__
        init_args = inspect.getfullargspec(self.__init__).args
        init_string = [f'{arg}={self.__dict__[arg]!r}'
                       for arg in init_args if arg in self.__dict__]
        return f'{cls}({", ".join(init_string)})'

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return exc_type is None

    def start(self):
        self.sock.listen()

    def stop(self):
        self.sock.close()

    def accept(self):
        conn, addr = self.sock.accept()
        return Connection(conn)
