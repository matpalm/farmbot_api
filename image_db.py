# image db helper

import sqlite3
import json

class ImageDB(object):

  def __init__(self, image_db_file='imgs/image.db', check_same_thread=True):
    self.conn = sqlite3.connect(image_db_file, check_same_thread=check_same_thread)

  def create_if_required(self):
    # called once to create db
      c = self.conn.cursor()
      try:
        c.execute('''create table imgs (
                          id integer primary key autoincrement,
                          farmbot_id integer,
                          capture_time text,
                          x integer,
                          y integer,
                          z integer,
                          api_response text,
                          filename text
                     )''')
      except sqlite3.OperationalError:
        # assume table already exists? clumsy...
        pass

  def has_record_for_farmbot_id(self, farmbot_id):
    c = self.conn.cursor()
    c.execute("select farmbot_id from imgs where farmbot_id=?", (farmbot_id,))
    return c.fetchone() is not None

  def imgs_for_coords(self, x, y, z):
    c = self.conn.cursor()
    if z is None:
      c.execute("select id, x, y, z, filename from imgs where x=? and y=? order by capture_time", (x, y, ))
    else:
      c.execute("select id, x, y, z, filename from imgs where x=? and y=? and z=? order by capture_time", (x, y, z, ))
    return c.fetchall()

  def insert(self, api_response, dts, filename):
    farmbot_id = api_response['id']
    capture_time = dts.strftime("%Y-%m-%d %H:%M:%S")
    x, y, z = map(int, [api_response['meta'][c] for c in ['x', 'y', 'z']])
    c = self.conn.cursor()
    insert_values = (farmbot_id, capture_time, x, y, z, json.dumps(api_response), filename)
    c.execute("insert into imgs (farmbot_id, capture_time, x, y, z, api_response, filename) values (?,?,?,?,?,?,?)", insert_values)
    self.conn.commit()

  def x_y_counts(self, min_c=1):
    c = self.conn.cursor()
    c.execute("select x, y, count(*) as c from imgs group by x, y having c >= ?", (min_c,))
    records = c.fetchall()
    return sorted(records, key=lambda r: -r[2])  # return sorted by freq
