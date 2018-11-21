# image db helper

import sqlite3
import json

class ImageDB(object):

  def __init__(self, image_db_file='image.db', check_same_thread=True):
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

#  def has_been_created(self):
#    c = self.conn.cursor()
#    c.execute("select name from sqlite_master where type='table' AND name='imgs';")
#    return c.fetchone() is not None

  def has_record_for_farmbot_id(self, farmbot_id):
    c = self.conn.cursor()
    c.execute("select farmbot_id from imgs where farmbot_id=?", (farmbot_id,))
    return c.fetchone() is not None

  def insert(self, api_response, dts, filename):
    farmbot_id = api_response['id']
    capture_time = dts.strftime("%Y-%m-%d %H:%M:%S")
    x, y, z = map(int, [api_response['meta'][c] for c in ['x', 'y', 'z']])
    c = self.conn.cursor()
    insert_values = (farmbot_id, capture_time, x, y, z, json.dumps(api_response), filename)
#    print("I", insert_values)
    c.execute("insert into imgs (farmbot_id, capture_time, x, y, z, api_response, filename) values (?,?,?,?,?,?,?)", insert_values)
    self.conn.commit()



#  def _id_for_img(self, img):
#    c = self.conn.cursor()
#    c.execute("select id from imgs where filename=?", (img,))
#    id = c.fetchone()
#    if id is None:
#      return None
#    else:
#      return id[0]

#  def _create_row_for_img(self, img):
#    c = self.conn.cursor()
#    c.execute("insert into imgs (filename) values (?)", (img,))
#    self.conn.commit()
#    return self._id_for_img(img)

#  def _delete_labels_for_img_id(self, img_id):
#    c = self.conn.cursor()
#    c.execute("delete from labels where img_id=?", (img_id,))
#    self.conn.commit()

#  def _add_rows_for_labels(self, img_id, labels, flip=False):
#    c = self.conn.cursor()
#    for x, y in labels:
#      if flip:
#        # TODO: DANGER WILL ROBERTSON! the existence of this, for the population
#        #       of db from centroids_of_connected_components denotes some inconsistency
#        #       somewhere... :/
#        x, y = y, x
#      c.execute("insert into labels (img_id, x, y) values (?, ?, ?)", (img_id, x, y,))
#    self.conn.commit()


#if __name__ == "__main__":
#  import argparse
#  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#  parser.add_argument('--label-db', type=str, default="label.db")
#  opts = parser.parse_args()
#  db = LabelDB(label_db_file=opts.label_db)
#  print("\n".join(db.imgs()))
