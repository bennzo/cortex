import socket
import struct


class Connection:
    data_sz_fmt = '<L'

    def __init__(self, socket):
        self.sock = socket

    def __repr__(self):
        cls = type(self).__name__
        sockname = ':'.join(map(str, self.sock.getsockname()))
        peername = ':'.join(map(str, self.sock.getpeername()))
        return f'<{cls} from {sockname} to {peername}>'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return exc_type is None

    @classmethod
    def connect(cls, host, port):
        sock = socket.socket()
        sock.connect((host, port))
        return cls(sock)

    def send(self, data):
        data_size = struct.pack(Connection.data_sz_fmt, len(data))
        sent = self.sock.sendall(data_size + data)
        return sent

    def receive(self, size=None):
        if size is None:
            data_size = self.receive(size=struct.calcsize(Connection.data_sz_fmt))
            size = struct.unpack(Connection.data_sz_fmt, data_size)[0]
        data = b''
        while len(data) < size:
            chunk = self.sock.recv(size - len(data))
            if not chunk:
                raise Exception(f'recieved {len(data)} bytes, expected {size} bytes')
            data += chunk
        return data

    def close(self):
        self.sock.close()
