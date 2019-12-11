import datetime
from ..utils import Connection
from brain import Thought

HEADER_FORMAT = '<QQL'


def upload_thought(address, user, thought):
    host, port = tuple(address.split(':'))
    try:
        with Connection.connect((host, int(port))) as conn:
            conn.send(Thought(int(user), datetime.datetime.now(), thought).serialize())
    except Exception as e:
        print(f'ERROR: {e}')
        return 1
