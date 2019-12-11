import inspect
import struct
from datetime import datetime

HEADER_FORMAT = '<QQL'


class Thought:
    """Encapsulates ``Thought`` objects"""
    def __init__(self, user_id, timestamp, thought):
        self.user_id = user_id
        self.timestamp = timestamp
        self.thought = thought

    def __repr__(self):
        cls = type(self).__name__
        init_args = inspect.getfullargspec(self.__init__).args
        init_string = [f'{arg}={self.__dict__[arg]!r}'
                       for arg in init_args if arg in self.__dict__]
        return f'{cls}({", ".join(init_string)})'

    def __str__(self):
        return f'[{self.timestamp}] user {self.user_id}: {self.thought}'

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.__dict__ == other.__dict__
        return False

    def serialize(self):
        msg = b''
        thought_enc = self.thought.encode()
        header_enc = struct.pack(HEADER_FORMAT,
                                 self.user_id,
                                 int(self.timestamp.timestamp()),
                                 len(thought_enc))
        msg += header_enc + thought_enc
        return msg

    def deserialize(data):
        uid, ts, thought_size = struct.unpack(HEADER_FORMAT, data[:20])
        ts = datetime.fromtimestamp(ts)
        thought = data[20:20+thought_size].decode()
        return Thought(uid, ts, thought)
