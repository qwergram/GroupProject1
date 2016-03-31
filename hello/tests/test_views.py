# coding=utf-8
from django.test import TransactionTestCase
# Must call test hello.views.test because there is something in django that
# uses the same name.
import hello.views
from hello.views import (
    index,
    detail
)


class TestViews(TransactionTestCase):
    # XXX Because we're modifying the code as we speak, I left four basic tests
    # XXX to increase coverage %.

    def test_default_view_response_code(self):
        response = index(None)
        self.assertTrue(response.status_code == 200)

    def test_default_view_ticker_exists(self):
        response = index(None)
        self.assertIn("<marquee>", response.content.decode())
        self.assertIn("</marquee>", response.content.decode())

    def test_detail_view_response_code(self):
        response = detail(None)
        self.assertTrue(response.status_code == 200)

    def test_check_view_response_code(self):
        response = hello.views.test(None, u"stocktwit", u"MSFT")
        self.assertTrue(response.status_code == 200)

    def test_twitter_response_code(self):
        response = hello.views.test(None, u"twitter", u"MSFT")
        self.assertTrue(response.status_code == 200)

    def test_reddit_response_code(self):
        response = hello.views.test(None, u"reddit", u"MSFT")
        self.assertTrue(response.status_code == 200)

    def test_nonexistent_response_code(self):
        response = hello.views.test(None, u"facebook", u"MSFT")
        self.assertTrue(response.status_code == 404)
