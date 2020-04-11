import importlib
from ..utils import parse_url


_CONFIG = {'PARSERS': ['pose', 'image_color', 'image_depth', 'feelings'],
           'DATA_FOLDER': 'data/temp'}


class Server:
    """ A Simple server that recieves messages and publishes them using a publish function.


    Attributes:
        host (:obj:`str`): Hostname of the server
        port (:obj:`int`): Port of the server
        publish (function): Publish function, takes a message and publishes it

    Args:
        host (:obj:`str`): Hostname of the server
        port (:obj:`int`): Port of the server
        publish (:obj:`function`): Publish function, takes a message and publishes it

    Routes:
        GET:
            - /config: Returns the server supported parsers
        POST:
            - /snapshot: Recieves a message and publishes it
    """
    def __init__(self, host, port, publish):
        self.host = host
        self.port = port
        self.publish = publish

        self.app = importlib.import_module(name=f'.app', package='cortex.server').app
        self.app.config.update(_CONFIG)
        self.app.config.update(PUBLISH_MESSAGE=publish)

    def start(self, **kwargs):
        """Runs the server.

        Args:
            **kwargs: Any keyword arguments that Flask.app.run() might take.
        """
        self.app.run(host=self.host, port=self.port, **kwargs)


def _cli_run_server(host, port, message_queue):
    # Import a message queue module according to the url scheme
    # and instantiate an appropriate client
    mq_scheme, mq_host, mq_port = parse_url(message_queue)
    mq_module = importlib.import_module(name=f'..net.mq.{mq_scheme}', package='cortex.server')
    publish = mq_module.SnapshotClient(mq_host, mq_port, **_CONFIG).publish
    run_server(host, port, publish)


def run_server(host, port, publish, threaded=True):
    """Initiates and runs a server.

    The server will run on the host:port given and publish each message recieved using the publish function passed.

    Args:
        host (:obj:`str`): Hostname of the server
        port (:obj:`int`): Port of the server
        publish (:obj:`function`): Publish function, takes a message and publishes it
        threaded (:obj:`bool`, optional): Flag for multi-thread use
    """
    server = Server(host, port, publish)
    server.start(threaded=threaded)
