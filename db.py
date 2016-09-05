import sqlite3
import numpy as np
import pandas as pd
import time

_DB_NAME = 'local.db'
_TABLE_NAME = 'stats'


class Database(object):
  def __init__(self, db_path=_DB_NAME):
    self.connection = sqlite3.connect(db_path, check_same_thread=False)
    # Create table if not existing.
    if not self.CheckTableExists():
      print 'Table %s does not exist, creating it...' % _TABLE_NAME
      self.CreateTable()

  def CheckTableExists(self):
    cursor = self.connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM sqlite_master WHERE type == "table" AND name == "{0}"'.format(_TABLE_NAME))
    ret = cursor.fetchone()[0] == 1
    cursor.close()
    return ret

  def CreateTable(self):
    cursor = self.connection.cursor()
    cursor.execute('CREATE TABLE {0} (time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ping_ms REAL, down_mbits REAL, up_mbits REAL)'.format(_TABLE_NAME))
    cursor.close()

  def Insert(self, ping_ms, down_mbits, up_mbits):
    cursor = self.connection.cursor()
    cursor.execute('INSERT INTO {0} (ping_ms, down_mbits, up_mbits) VALUES ({1}, {2}, {3})'.format(_TABLE_NAME, ping_ms, down_mbits, up_mbits))
    self.connection.commit()
    cursor.close()

  def Get(self, duration=3600, timezone_offset=0):
    # Get max timestamp.
    cursor = self.connection.cursor()
    cursor.execute('SELECT MAX(time) FROM {0}'.format(_TABLE_NAME))
    row = cursor.fetchone()
    if not row:
      raise RuntimeError('There are no entries in the database yet')
    last_timestamp = row[0]
    rows = cursor.execute('SELECT * FROM {0} WHERE CAST(STRFTIME("%s", time) AS INT) >= CAST(STRFTIME("%s", "{1}") AS INT) - {2}'.format(_TABLE_NAME, last_timestamp, duration))
    data = []
    index = []
    for row in rows:
      index.append(pd.Timestamp(row[0]) + pd.Timedelta(minutes=timezone_offset))
      data.append((row[1], row[2], row[3]))
    df = pd.DataFrame(data, index=index, columns=('ping_ms', 'down_mbits', 'up_mbits'))
    cursor.close()
    return df


if __name__ == '__main__':
  db = Database()
  print db.Get(2)
