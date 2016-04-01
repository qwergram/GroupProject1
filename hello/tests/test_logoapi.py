# coding=utf-8
from django.test import TransactionTestCase
from hello.logo_grab import (
    get_endpoint,
    get_response,
    handle_response,
    get_domain,
    get_logo,
)

try:
    ConnectionError
except NameError:
    ConnectionError = ValueError

class MockResponse():
    ok = True


with open("hello/testdata/msft2.html") as h:
    response = MockResponse()
    response.text = h.read()
with open("hello/testdata/msft3.html") as h:
    bad_response = MockResponse()
    bad_response.ok = False
    bad_response.text = h.read()


class TickerTest(TransactionTestCase):

    def test_get_endpoint(self):
        self.assertEqual(get_endpoint("MSFT"), "http://finance.yahoo.com/q/pr?s=msft")

    def test_handle_response(self):
        self.assertEqual(handle_response(response), "http://www.microsoft.com")

    def test_handle_bad_response(self):
        with self.assertRaises(ConnectionError):
            handle_response(bad_response)
