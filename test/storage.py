import ujson

from unittest import TestCase
from mashape_analytics import Storage

storage = Storage()
with open('test/fixtures/storage.json') as file:
  fixtures = ujson.load(file)

class StorageTest(TestCase):
  def setUp(self):
    storage.reset()

    for fixture in fixtures:
      storage._execute_('INSERT INTO alfs (alf) VALUES (?)', (ujson.dumps(fixture),))

  def tearDown(self):
    pass

  def test_should_count(self):
    self.assertEqual(len(fixtures), storage.count())

  def test_should_recover_from_corrupt_database(self):
    pass

  def test_should_put_alf_into_storage(self):
    storage.put({'test': 'test'})
    row = storage._fetch_one_('SELECT COUNT(1) FROM alfs')
    self.assertEqual(len(fixtures) + 1, row[0])

  def test_should_get_alfs_into_storage(self):
    storage.get_batch_and_delete(3)
    pass
