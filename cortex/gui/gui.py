from .app import app


def run_server(host='127.0.0.1', port=8080, api_host='127.0.0.1', api_port=5000):
    app.config.update({'API_HOST': api_host, 'API_PORT': api_port})
    app.run(host=host, port=port, threaded=True)
