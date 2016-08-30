import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import threading

_DPI = 72
_FORMAT = 'png'

# This class needs to be thread-safe. Otherwise image are garbled :(
_GLOBAL_LOCK = threading.Lock()


class Plotter(object):
  def __init__(self, db):
    self.db = db

  def Bandwidth(self, duration, width=640, height=480):
    with _GLOBAL_LOCK:
      _, ax = _CreateFigure(width, height)
      df = self.db.Get(duration=duration)
      df[['down_mbits', 'up_mbits']].plot(ax=ax)
      ax.set_ylim(bottom=0)
      return _GetImageContent()

  def Ping(self, duration, width=640, height=480):
    with _GLOBAL_LOCK:
      _, ax = _CreateFigure(width, height)
      df = self.db.Get(duration=duration)
      df[['ping_ms']].plot(ax=ax)
      ax.set_ylim(bottom=0)
      return _GetImageContent()


def _CreateFigure(width=640, height=480):
  return plt.subplots(figsize=(float(width) / float(_DPI), float(height) / float(_DPI)), dpi=_DPI)


def _GetImageContent():
  plt.tight_layout()
  image_buffer = io.BytesIO()
  plt.savefig(image_buffer, format=_FORMAT)
  image_buffer.seek(0)
  content = image_buffer.read()
  return content
