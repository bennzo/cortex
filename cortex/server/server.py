import importlib
from flask import request
# from .app import app
from ..utils import parse_url


# TODO: move configurations to external files
_CONFIG = {'PARSERS': ['pose', 'image_color', 'image_depth', 'feelings'],
           'DATA_FOLDER': 'data/temp'}


class Server:
    def __init__(self, host, port, publish):
        self.host = host
        self.port = port
        self.publish = publish

        self.app = importlib.import_module(name=f'.app', package='cortex.server').app
        self.app.config.update(_CONFIG)
        self.app.config.update(PUBLISH_MESSAGE=publish)

    def start(self, **kwargs):
        self.app.run(host=self.host, port=self.port, **kwargs)


def _cli_run_server(host, port, message_queue):
    # Import a message queue module according to the url scheme
    # and instantiate an appropriate client
    mq_scheme, mq_host, mq_port = parse_url(message_queue)
    mq_module = importlib.import_module(name=f'..net.mq.{mq_scheme}', package='cortex.server')
    publish = mq_module.SnapshotClient(mq_host, mq_port, **_CONFIG).publish
    run_server(host, port, publish)


def run_server(host, port, publish, threaded=False):
    server = Server(host, port, publish)
    server.start(threaded=threaded)
    # app.run(host=host, port=port, debug=False, use_debugger=False, use_reloader=False, passthrough_errors=True)
