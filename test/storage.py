import ujson
import time

from unittest import TestCase
from mashape_analytics.storage import Storage

storage = Storage()
with open('test/fixtures/storage.json') as file:
  fixtures = ujson.load(file)

class StorageTest(TestCase):
  def setUp(self):
    storage.reset()
    assert self.queue_count() == 0

    for fixture in fixtures:
      storage._execute_('INSERT INTO queue (json) VALUES (?)', (ujson.dumps(fixture),))

    assert self.queue_count() == len(fixtures)

  def tearDown(self):
    pass

  def queue_count(self):
    return storage._fetch_one_('SELECT COUNT(1) FROM queue')[0]

  def test_should_count(self):
    self.assertEqual(len(fixtures), storage.count())

  def test_should_get_oldest_time(self):
    # should be between 0 and 1s
    delta_time = time.time() - storage.oldest_time()
    self.assertGreater(1, delta_time)
    self.assertGreater(delta_time, 0)

  def test_should_put_obj_into_storage(self):
    storage.put({'test': 'test'})

    self.assertEqual(self.queue_count(), len(fixtures) + 1) # one more

  def test_should_put_multiple_objs_into_storage(self):
    storage.put_all([{'test': 'test_1'}, {'test': 'test_2'}])

    self.assertEqual(self.queue_count(), len(fixtures) + 2) # two more

  def test_should_get_objs_in_storage(self):
    rows = storage.get(len(fixtures))
    self.assertEqual(len(fixtures), len(rows))

    for index, row in enumerate(rows):
      self.assertEqual(row[1], fixtures[index])

  def test_should_delete_obj(self):
    id = storage._fetch_one_('SELECT id FROM queue LIMIT 1')[0]
    storage.delete([id])

    self.assertEqual(self.queue_count(), len(fixtures) - 1) # deleted one

  def test_should_get_then_delete(self):
    rows = storage.get_then_delete(len(fixtures))
    self.assertEqual(len(fixtures), len(rows))

    for index, row in enumerate(rows):
      self.assertEqual(row[1], fixtures[index])

    self.assertEqual(self.queue_count(), 0) # deleted all
