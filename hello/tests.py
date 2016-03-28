from django.test import TestCase
from .stocktwits import get_stock_comments

# Create your tests here.

class StockTwitsCase(TestCase):

    def test_error_is_raised(self):
        with self.assertRaises(ValueError):
            get_stock_comments("not a real company")

    def test_response_length(self):
        response = get_stock_comments("MSFT")
        self.assertEqual(len(response), 30)

    def test_response_contains_id(self):
        response = get_stock_comments("MSFT")
        for r in response:
            self.assertNotEqual(r.get('id'), None)

    def test_response_contains_body(self):
        response = get_stock_comments("MSFT")
        for r in response:
            self.assertNotEqual(r.get('body'), None)
