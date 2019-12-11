import socket


class Connection:
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
        sent = self.sock.sendall(data)
        return sent

    def receive(self, size):
        data = b''
        while len(data) < size:
            chunk = self.sock.recv(size - len(data))
            if not chunk:
                raise Exception(f'recieved {len(data)} bytes, expected {size} bytes')
            data += chunk
        return data

    def close(self):
        self.sock.close()
