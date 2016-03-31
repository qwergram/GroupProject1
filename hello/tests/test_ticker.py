# coding=utf-8
from django.test import Client, TransactionTestCase
import json

class TickerTest(TransactionTestCase):

    def test_check_view_content(self):
        with open("hello/testdata/msft1.json") as f:
            json_blob = json.loads(f.read())
        self.assertTrue(isinstance(json_blob, list))
        self.assertTrue(isinstance(json_blob[0], dict))
        self.assertIn('author', json_blob[0])
        self.assertIn('content', json_blob[0])
        self.assertIn('social_id', json_blob[0])
        self.assertIn('url', json_blob[0])
        self.assertIn('urls', json_blob[0])
        self.assertIn('popularity', json_blob[0])
        self.assertIn('source', json_blob[0])
        self.assertIn('created_time', json_blob[0])
        self.assertIn('symbols', json_blob[0])
        self.assertIn('focus', json_blob[0])
        self.assertIn('author_image', json_blob[0])
