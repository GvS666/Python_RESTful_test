import base64
import json
import unittest

from pymongo import MongoClient

import main


class FlaskrTestCase(unittest.TestCase):

  def setUp(self):
    main.app.testing = True
    self.app = main.app.test_client()

  def tearDown(self):
    client = MongoClient(main.app.config['MONGO_URI'])
    client.drop_database('test')

  def open_with_auth(self, url, method, **kwargs):
    return self.app.open(url,
                         method=method,
                         headers={
                           'Authorization': 'Basic ' + base64.b64encode(bytes("admin:admin", 'ascii')).decode('ascii')
                         }, **kwargs
                         )

  def test_get_users(self):
    resp = self.app.get('/prt/api/v1.0/users')
    self.assertEqual(resp.status_code, 403)

    resp = self.open_with_auth('/prt/api/v1.0/users', 'GET')
    self.assertEqual(resp.status_code, 200)


  def test_create_user(self):
    resp = self.app.post('/prt/api/v1.0/users')
    self.assertEqual(resp.status_code, 403)

    resp = self.open_with_auth('/prt/api/v1.0/users', 'POST',
                               data=json.dumps({
	"firstname": "aaa",
	"lastname": "zzzz",
	"latitude": "51.657195868652785",
	"longitude": "-3.9440917943750264"
}),
                               content_type='application/json')
    self.assertEqual(resp.status_code, 201)
