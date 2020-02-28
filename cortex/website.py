import re
from http.server import HTTPServer, BaseHTTPRequestHandler


def WRHFactory(router):
    class WebsiteRequestHandler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.router = router
            super(WebsiteRequestHandler, self).__init__(*args, **kwargs)

        def do_GET(self):
            status, body = self.router(self.path)
            body = body.encode()
            self.send_response(status)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
    return WebsiteRequestHandler


class Website:
    def __init__(self):
        self.url_handlers = {}

    def route(self, path):
        def decorator(f):
            self.url_handlers[path] = f
            return f
        return decorator

    def request_dispatcher(self, path):
        for url, handler in self.url_handlers.items():
            matches = re.match('^'+url+'$', path)
            if matches is not None:
                return handler(*matches.groups())
        return 404, ""

    def run(self, address):
        with HTTPServer(address, WRHFactory(self.request_dispatcher)) as httpd:
            while True:
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    break
