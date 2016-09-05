import argparse
import BaseHTTPServer
import SocketServer
import os
import urlparse

import db
import plotter
import speedtester


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

  def __init__(self, server_handle, *args, **kwargs):
    self.server_handle = server_handle
    BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

  def do_GET(self):
    parsed_url = urlparse.urlparse(self.path)
    path = parsed_url.path
    params = urlparse.parse_qs(parsed_url.query)
    # Main page.
    if path in self.server_handle.content:
      # Default header.
      self.send_response(200)
      self.send_header('Content-type', self.server_handle.content_type[path])
      self.end_headers()
      self.wfile.write(self.server_handle.content[path])
      self.wfile.close()
      return

    # If it is not a regular static file. Output plot.
    if path == '/bandwidth' or path == '/ping':
      duration_sec = params['duration'][0]
      img_width = int(params['width'][0])
      img_height = int(params['height'][0])
      offset_mins = int(params['offset'][0])
      self.send_response(200)
      self.send_header('Content-type', 'image/png')
      self.end_headers()
      if path == '/bandwidth':
        self.wfile.write(self.server_handle.plotter.Bandwidth(duration_sec, img_width, img_height, timezone_offset=offset_mins))
      elif path == '/ping':
        self.wfile.write(self.server_handle.plotter.Ping(duration_sec, img_width, img_height, timezone_offset=offset_mins))
      self.wfile.close()


def CreateHandler(server_handle):
  return lambda *args, **kwargs: RequestHandler(server_handle, *args, **kwargs)


class ThreadedHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
  """Handle requests in a separate thread."""


class Server(object):

  def __init__(self, directory, host='localhost', port=8080, interval=5*60, db_path='local.db'):
    self.host = host
    self.port = port
    # Load all content in memory.
    self.content = {}
    self.content_type = {}
    with open(os.path.join(directory, 'index.html')) as fp:
      self.content['/'] = fp.read()
      self.content_type['/'] = 'text/html'
    with open(os.path.join(directory, 'favicon.ico')) as fp:
      self.content['/favicon.ico'] = fp.read()
      self.content_type['/favicon.ico'] = 'image/gif'
    # Connect to database.
    self.db = db.Database(db_path)
    self.plotter = plotter.Plotter(self.db)
    # Speedtest thread.
    self.speedtest = speedtester.Speedtester(interval=interval, db_path=db_path)

  def Start(self):
    try:
      self.speedtest.Start()
      server = ThreadedHTTPServer((self.host, self.port), CreateHandler(self))
      print 'Server started: http://%s:%d.' % (self.host, self.port)
      server.serve_forever()
    except KeyboardInterrupt:
      print 'Shutting down server.'
      server.socket.close()
      self.speedtest.Stop()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--root", metavar='DIRECTORY', type=str, required=True, help="The root directory where the client files are located.")
  parser.add_argument("--host", metavar='IP', type=str, default='localhost', help="The server hostname.")
  parser.add_argument("--port", metavar='PORT', type=int, default=8080, help="The server port.")
  parser.add_argument("--interval", metavar='SECONDS', type=int, default=5*60, help="The interval between measurements.")
  parser.add_argument("--db", metavar='PATH', type=str, default='local.db', help="Path to SQLITE database file.")
  args = parser.parse_args()
  server = Server(args.root, host=args.host, port=args.port, interval=args.interval, db_path=args.db)
  server.Start()
