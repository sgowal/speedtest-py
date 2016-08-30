import threading
import time
import os

import db


class Speedtester(object):
  def __init__(self, interval=5*60):
    self.thread = SpeedtesterThread(interval)

  def Start(self):
    self.thread.start()

  def Stop(self):
    self.thread.Stop()
    self.thread.join()


class SpeedtesterThread(threading.Thread):
  def __init__(self, interval):
    threading.Thread.__init__(self)
    self.must_stop = False
    self.must_stop_lock = threading.Lock()
    self.interval = interval
    self.db = db.Database()

  def run(self):
    print 'Speedtest started'
    last_measurement = time.time()
    self.must_stop_lock.acquire()
    while not self.must_stop:
      self.must_stop_lock.release()

      # Run speedtest.
      current_time = time.time()
      if current_time - last_measurement >= self.interval:
        print 'Running speed test...'
        last_measurement = time.time()
        ping_ms, down_mbits, up_mbits = _RunSpeedtest()
        print ping_ms, down_mbits, up_mbits
        self.db.Insert(ping_ms, down_mbits, up_mbits)

      time.sleep(1)
      self.must_stop_lock.acquire()
    self.must_stop_lock.release()
    print 'Speedtest stopped'

  def Stop(self):
    self.must_stop_lock.acquire()
    self.must_stop = True
    self.must_stop_lock.release()


def _RunSpeedtest():
  output_stdout = os.popen("speedtest-cli --simple").read()
  if 'Cannot' in output_stdout:
    return None
  # Parse results (not very robust).
  # Result:
  # Ping: 529.084 ms
  # Download: 0.52 Mbit/s
  # Upload: 1.79 Mbit/s
  output_lines = output_stdout.split('\n')
  ping_ms = output_lines[0]
  down_mbits = output_lines[1]
  up_mbits = output_lines[2]
  ping_ms = float(ping_ms.replace('Ping: ', '').replace(' ms', ''))
  down_mbits = float(down_mbits.replace('Download: ', '').replace(' Mbits/s', ''))
  up_mbits = float(up_mbits.replace('Upload: ', '').replace(' Mbits/s', ''))
  return ping_ms, down_mbits, up_mbits
