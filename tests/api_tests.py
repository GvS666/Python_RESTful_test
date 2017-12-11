import base64
import unittest

from flask_pymongo import PyMongo
from pymongo import MongoClient

import main


class FlaskrTestCase(unittest.TestCase):

  def setUp(self):
    main.app.config['MONGO_DBNAME'] = 'test'
    main.app.testing = True
    main.mongo_mgr = PyMongo(main.app)
    self.app = main.app.test_client()

  def tearDown(self):
    client = MongoClient(main.app.config['MONGO_URI'])
    client.drop_database('test')

  def open_with_auth(self, url, method):
    return self.app.open(url,
                         method=method,
                         headers={
                           'Authorization': 'Basic ' + base64.b64encode(bytes("admin:admin", 'ascii')).decode('ascii')
                         }
                         )

  def test_get_users(self):
    resp = self.app.get('/prt/api/v1.0/users')
    self.assertEqual(resp.status_code, 403)

    resp = self.open_with_auth('/prt/api/v1.0/users', 'GET')
    self.assertEqual(resp.status_code, 200)
