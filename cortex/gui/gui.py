from .app import app


def run_server(host='127.0.0.1', port=8080, api_host='127.0.0.1', api_port=5000):
    """Sets up a GUI web-server which exposes the API server

    Args:
        host (:obj:`str`): Hostname of the GUI server
        port (:obj:`int`): Port of the GUI server
        api_host (:obj:`str`): Hostname of the API server
        api_port (:obj:`int`): Port of the API server
    """
    app.config.update({'API_HOST': api_host, 'API_PORT': api_port})
    app.run(host=host, port=port, threaded=True)
