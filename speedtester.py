import threading
import time
import os

import db
import speedtest_cli


class Speedtester(object):
  def __init__(self, interval=5*60, db_path='local.db'):
    self.thread = SpeedtesterThread(interval, db_path)

  def Start(self):
    self.thread.start()

  def Stop(self):
    self.thread.Stop()
    self.thread.join()


class SpeedtesterThread(threading.Thread):
  def __init__(self, interval, db_path):
    threading.Thread.__init__(self)
    self.must_stop = False
    self.must_stop_lock = threading.Lock()
    self.interval = interval
    self.db = db.Database(db_path)

  def run(self):
    print 'Speedtest started'
    last_measurement = time.time() - self.interval  # Make first measurement immediately.
    self.must_stop_lock.acquire()
    while not self.must_stop:
      self.must_stop_lock.release()

      # Run speedtest.
      current_time = time.time()
      if current_time - last_measurement >= self.interval:
        print 'Running speed test...'
        last_measurement = time.time()
        successful = False
        while not successful:
          try:
            ping_ms, down_mbits, up_mbits = speedtest_cli.Speedtest(verbose=True)
            print ping_ms, down_mbits, up_mbits
            successful = True
          except speedtest_cli.SpeedtestCliServerListError:
            print 'Cannot list speedtest servers'
        self.db.Insert(ping_ms, down_mbits, up_mbits)
      time.sleep(1)
      self.must_stop_lock.acquire()
    self.must_stop_lock.release()
    print 'Speedtest stopped'

  def Stop(self):
    self.must_stop_lock.acquire()
    self.must_stop = True
    self.must_stop_lock.release()
