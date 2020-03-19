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
    setup_app(database_url=database_url)
    # app.run(host=host, port=port, threaded=threaded)
    app.run(host=host, port=port, debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True)

