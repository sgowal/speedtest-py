import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import threading

_DPI = 72
_FORMAT = 'png'

# This class needs to be thread-safe. Otherwise image are garbled :(
_GLOBAL_LOCK = threading.Lock()


class Plotter(object):
  def __init__(self, db):
    self.db = db

  def Bandwidth(self, duration, width=640, height=480, timezone_offset=0):
    with _GLOBAL_LOCK:
      _, ax = _CreateFigure(width, height)
      df = self.db.Get(duration=duration, timezone_offset=timezone_offset)
      df = df[['down_mbits', 'up_mbits']]
      df.plot.area(stacked=False, ax=ax)
      up_mbits = df.up_mbits.values[-1]
      down_mbits = df.down_mbits.values[-1]
      avg_up_mbits = np.mean(df.up_mbits)
      avg_down_mbits = np.mean(df.down_mbits)
      ax.set_title('(Latest) Download: %.1f Mbits/s - Upload: %.1f Mbits/s\n'
                   '(Average) Download: %.1f Mbits/s - Upload: %.1f Mbits/s' % (down_mbits, up_mbits, avg_down_mbits, avg_up_mbits))
      ax.set_ylim(bottom=0)
      return _GetImageContent()

  def Ping(self, duration, width=640, height=480, timezone_offset=0):
    with _GLOBAL_LOCK:
      _, ax = _CreateFigure(width, height)
      df = self.db.Get(duration=duration, timezone_offset=timezone_offset)
      df = df[['ping_ms']]
      df.plot(ax=ax)
      ping_ms = df.ping_ms.values[-1]
      avg_ping_ms = np.mean(df.ping_ms)
      ax.set_title('Latest: %.1f ms - Average: %.1f ms' % (ping_ms, avg_ping_ms))
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
