import importlib
from .app import app
from ..utils import parse_url


def setup_app(database_url):
    # Initialize DB Client
    scheme, host, port = parse_url(database_url)
    db_module = importlib.import_module(name=f'..net.db.{scheme}', package='cortex.api')
    db_client = db_module.APIClient(host, port)
    app.config.update(DB_CLIENT=db_client)


def run_api_server(host='127.0.0.1', port=5000, database_url='mongodb://127.0.0.1:27017'):
    """Sets up an API server which exposes the given database

    Initialized by a database url in the format <mq_name>://<host>:<port>.
    The api client is dynamically imported from the :mod:`cortex.net.db` module and
    has to be implemented in the appropriate sub-module.
    for example: passing 'mongodb://127.0.0.1:27017' as db_url, an APIClient
    will be imported from :mod:`cortex.net.db.mongodb` and instantiated.

    Args:
        host (:obj:`str`): Hostname of the API server
        port (:obj:`int`): Port of the API server
        database_url (:obj:`str`): Database URL in the format <db_name>://<host>:<port>
    """
    setup_app(database_url=database_url)
    app.run(host=host, port=port, threaded=True)
    # app.run(host=host, port=port, debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True)

