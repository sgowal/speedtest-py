import threading
import time
import os

import db
import speedtest_cli


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
        ping_ms, down_mbits, up_mbits = speedtest_cli.Speedtest()
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
