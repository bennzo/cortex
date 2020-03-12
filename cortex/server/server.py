import importlib
from .app import app
from ..utils import parse_url


_CONFIG = {'PARSERS': ['pose', 'image_color', 'image_depth', 'feelings'],
           'DATA_FOLDER': 'data/temp'}


# TODO: Check if both publish and message_queue is None
def setup_app(publish=None, message_queue=None):
    app.config.update(_CONFIG)
    if publish is None:
        scheme, host, port = parse_url(message_queue)
        # Import a message queue module according to the url scheme
        # and instantiate an appropriate client
        mq_module = importlib.import_module(name=f'..net.mq.{scheme}',
                                            package='cortex.server')
        publish = mq_module.SnapshotClient(host, port, **_CONFIG).publish
    app.config.update(PUBLISH_MESSAGE=publish)


def _cli_run_server(host, port, message_queue):
    setup_app(message_queue=message_queue)
    app.run(host=host, port=port, threaded=False)
    

def run_server(host, port, publish, threaded=False):
    setup_app(publish=publish)
    # app.run(host=host, port=port, threaded=threaded)
    app.run(host=host, port=port, debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True)
