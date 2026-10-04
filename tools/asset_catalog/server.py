"""Read-only local file serving; refreshing only writes the disposable index."""
import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit

from .index import CatalogIndex, ROOT


def serve(root=ROOT, port=8000):
    index = CatalogIndex(root)
    index.refresh()
    lock = threading.Lock()

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            path = unquote(urlsplit(self.path).path)
            if path == '/api/catalog':
                try:
                    with lock:
                        content = json.dumps(index.refresh()).encode()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                except (OSError, ValueError) as error:
                    self.send_error(503, f'Index temporarily unavailable: {error}')
                return
            self.serve_file()

        def do_HEAD(self):
            self.serve_file(head=True)

        def serve_file(self, head=False):
            path = unquote(urlsplit(self.path).path)
            if path == '/':
                self.path = '/catalog/index.html'
                path = self.path
            target = (index.root / path.lstrip('/')).resolve()
            allowed = any(target.is_relative_to(index.root / folder)
                          for folder in ('catalog', 'exports', 'sources'))
            if not allowed or not target.is_file():
                self.send_error(404, 'File unavailable')
                return
            if head:
                super().do_HEAD()
            else:
                super().do_GET()

        def end_headers(self):
            # Even model-viewer's in-memory cache is bypassed by versioned URLs.
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            super().end_headers()

        def log_message(self, format, *args):
            if len(args) < 2 or str(args[1]) not in ('200', '304'):
                super().log_message(format, *args)

    server = ThreadingHTTPServer(('127.0.0.1', port),
                                partial(Handler, directory=str(index.root)))
    print(f'Asset catalog: http://127.0.0.1:{server.server_port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
