from .app import app


_CONFIG = {'PARSERS': ['pose', 'image_color', 'image_depth', 'feelings']}


def run_server(host, port, publish, threaded=False):
    app.config.update(_CONFIG)
    # app.run(host=host, port=port, threaded=threaded)
    app.run(host=host, port=port, debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True)
