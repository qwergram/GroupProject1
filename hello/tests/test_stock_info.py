# coding=utf-8
from datetime import datetime, timedelta

from django.test import TestCase
import json
import mock
import requests
from requests import RequestException
from hello.tests import load_data


# noinspection PyUnresolvedReferences
class StockInfoCase(TestCase):
    def test_yahoo_query(self):
        from hello.stock_info import _yahoo_query
        with mock.patch.object(requests, 'get') as get:
            get().json.return_value = {1: 1}
            self.assertEqual(_yahoo_query('asdf'), {1: 1})
            self.assertEqual(len(get().json.call_args_list), 1)
        with mock.patch.object(requests, 'get') as get:
            get.side_effect = RequestException
            self.assertEqual(_yahoo_query('asdf'), {})

    def test_yahoo_historical_range(self):
        from hello.stock_info import _yahoo_historical_range
        import hello.stock_info
        with mock.patch.object(hello.stock_info, '_yahoo_query') as yq:
            yq.return_value = {'query': {'results': {'stock': {
                'start': "2010-01-01",
                'end': "2010-12-31",
            }}}}
            self.assertEqual(_yahoo_historical_range('asdf'), (datetime(2010, 1, 1), datetime(2010, 12, 31)))

    def test_yahoo_data(self):
        from hello.stock_info import _yahoo_top_movers, TopMover
        import hello.stock_info
        hello.stock_info._yahoo_cached = None  # ensure cache is cleared
        data = load_data("yahoo_data.htmlfragment")
        movers = _yahoo_top_movers(data)
        self.assertEqual(movers, [
            TopMover("SUNE", "SunEdison, Inc.", 0.57, -0.69, -54.76, 147037800),
            TopMover("BAC", "Bank of America Corporation", 13.42, -0.2, -1.47, 101526412),
            TopMover("HOLX", "Hologic Inc.", 34.5, -0.07, -0.2, 52960883),
            TopMover("ESV", "Ensco plc", 10.3, -0.42, -3.92, 51307639),
            TopMover("FCX", "Freeport-McMoRan Inc.", 10.14, 0, 0, 44196028),
            TopMover("CNC", "Centene Corp.", 62.6, 0.21, 0.34, 39208539),
            TopMover("GE", "General Electric Company", 31.48, -0.01, -0.03, 38548937),
            TopMover("CRC", "California Resources Corporation", 1.05, -0.12, -10.26, 35801398),
            TopMover("PFE", "Pfizer Inc.", 30.05, 0.27, 0.91, 34596186),
            TopMover("AAPL", "Apple Inc.", 107.68, 2.49, 2.37, 31176911),
            TopMover("MU", "Micron Technology, Inc.", 10.45, 0.07, 0.67, 30888521),
            TopMover("QQQ", "PowerShares QQQ ETF", 108.83, 1.72, 1.61, 29949401),
            TopMover("FB", "Facebook, Inc.", 116.14, 2.45, 2.15, 29812606),
            TopMover("CHK", "Chesapeake Energy Corporation", 4.04, -0.11, -2.65, 28456020),
            TopMover("PBR", "Petróleo Brasileiro S.A. - Petrobras", 5.83, 0.04, 0.69, 27202507),
            TopMover("VRX", "Valeant Pharmaceuticals International, Inc.", 28.98, 0.12, 0.42, 26872253),
            TopMover("ITUB", "Itaú Unibanco Holding S.A.", 8.73, 0.04, 0.46, 26874125),
            TopMover("F", "Ford Motor Co.", 13.2, 0.11, 0.84, 26062180),
            TopMover("T", "AT&T, Inc.", 39.45, 0.38, 0.97, 25892774),
            TopMover("KO", "The Coca-Cola Company", 46.48, 0.68, 1.48, 25009987),
        ])

    def test_top_movers(self):
        from hello.stock_info import top_movers, TopMover, _YAHOO_MOVERS_URL
        import hello.stock_info
        with mock.patch.object(requests, 'get') as get:
            with mock.patch.object(hello.stock_info, '_yahoo_top_movers') as ytm:
                ytm.return_value = [1, 2, 3]
                self.assertEqual(top_movers(), [1, 2, 3])
                # assert that calling it again immediately does not hit requests again because it caches
                top_movers()
                self.assertEqual(len(get.call_args_list), 1)
                # test what happens when requests fails
                hello.stock_info._yahoo_cached = None
                ytm.side_effect = RequestException
                self.assertEqual(top_movers(), [])

    def test_day_memory(self):
        from hello.stock_info import (
            _latest_remembered_entry, _remember_day, _remembered_historical,
            _yahoo_historical_range, Day
        )
        _remembered_historical.clear()
        self.assertTrue(_latest_remembered_entry('~~test~~') is None)
        day1 = Day(datetime(2015, 1, 1), 1, 1, 1, 1, 1, 1)
        day2 = Day(datetime(2015, 1, 2), 1, 1, 1, 1, 1, 1)
        _remember_day('~~TEST~~', day1)
        self.assertTrue(set(_remembered_historical) == {'~~test~~'})
        self.assertTrue(_latest_remembered_entry('~~test~~') == day1.date)
        self.assertTrue(_latest_remembered_entry('~~TEST~~') == day1.date)
        _remember_day('~~TEST~~', day2)
        self.assertTrue(set(_remembered_historical) == {'~~test~~'})
        self.assertTrue(_latest_remembered_entry('~~test~~') == day2.date)
        self.assertTrue(_latest_remembered_entry('~~TEST~~') == day2.date)
        _remember_day('~~TEST2~~', day1)
        self.assertTrue(set(_remembered_historical) == {'~~test~~', '~~test2~~'})

    def test_create_day(self):
        from hello.stock_info import Day
        self.assertTrue(Day.from_json({}) is None)
        self.assertTrue(Day.from_json({
            'Date': "2016-11-05",
            'Open': 5,
            'High': 10,
            'Low': 1,
            'Close': 4,
            'Volume': 100,
            'Adj_Close': 4.5
        }) == Day(datetime(2016, 11, 5), 5, 10, 1, 4, 100, 4.5))

    def test_break_up_range(self):
        from hello.stock_info import _MAX_FETCHED_DAYS, _break_up_fetch_range
        date = datetime(2000, 1, 1)
        self.assertEqual(
            list(_break_up_fetch_range(date, date)),
            [(date, date)]
        )
        start = date - timedelta(days=_MAX_FETCHED_DAYS * 1.5 // 1)
        self.assertEqual(
            list(_break_up_fetch_range(start, date)),
            [
                (start, start + timedelta(days=_MAX_FETCHED_DAYS - 1)),
                (start + timedelta(days=_MAX_FETCHED_DAYS), date)
            ]
        )
        self.assertEqual(
            list(_break_up_fetch_range(date, date - timedelta(days=1))),
            []
        )

    def test_fetch_yahoo_historical(self):
        from hello.stock_info import _fetch_yahoo_historical
        import hello.stock_info
        params = ('asdf', datetime(1, 1, 1), datetime(1, 1, 1))
        with mock.patch.object(requests, 'get') as get:
            get().json.return_value = json.loads(load_data("history4.json"))
            self.assertEqual(len(_fetch_yahoo_historical(params)[1]), 4)
            get().json.return_value = json.loads(load_data("history1.json"))
            self.assertEqual(len(_fetch_yahoo_historical(params)[1]), 1)
            get().json.return_value = json.loads(load_data("history0.json"))
            self.assertEqual(len(_fetch_yahoo_historical(params)[1]), 0)
            get().json.return_value = {}
            self.assertEqual(len(_fetch_yahoo_historical(params)[1]), 0)
            get().json.return_value = None
            self.assertEqual(len(_fetch_yahoo_historical(params)[1]), 0)
            get.side_effect = RequestException
            self.assertEqual(len(_fetch_yahoo_historical(params)[1]), 0)

    def test_fetch_stock_history(self):
        from hello.stock_info import fetch_stock_history, Day, _remembered_historical
        import hello.stock_info
        with mock.patch.object(hello.stock_info, '_yahoo_historical_range') as yhr:
            yhr.return_value = datetime(2010, 1, 1), datetime(2015, 1, 1)
            with mock.patch.object(hello.stock_info, '_break_up_fetch_range') as bfr:
                bfr.return_value = [(1, 2), (3, 4)]
                with mock.patch.object(hello.stock_info, '_fetch_yahoo_historical') as fyh:
                    day1 = Day(datetime(2010, 1, 1), 1, 1, 1, 1, 1, 1)
                    day2 = Day(datetime(2010, 1, 2), 1, 1, 1, 1, 1, 1)
                    # side_effect will yield from an iterable to return
                    fyh.side_effect = [
                        ('asdf', [day1, day2, None]),
                        ('asdf', [])
                    ]
                    _remembered_historical.clear()
                    fetch_stock_history('asdf')
                    self.assertEqual(
                        set(_remembered_historical['asdf'].items()),
                        {
                            (day1.date, day1),
                            (day2.date, day2)
                        }
                    )
            yhr.side_effect = RequestException
            fetch_stock_history('asdf')

    def test_get_stock_history(self):
        from hello.stock_info import get_stock_history, Day, _remembered_historical, _remember_day
        import hello.stock_info
        day1 = Day(datetime(2010, 1, 1), 1, 1, 1, 1, 1, 1)
        day2 = Day(datetime(2010, 1, 2), 1, 1, 1, 1, 1, 1)
        _remembered_historical.clear()
        _remember_day('~~test~~', day1)
        _remember_day('~~test~~', day2)
        self.assertEqual(get_stock_history('~~not test~~'), [])
        self.assertEqual(get_stock_history('~~test~~'), [day1, day2])
        self.assertEqual(get_stock_history('~~test~~', datetime(2011, 1, 1), datetime(2012, 1, 1)), [])
        self.assertEqual(get_stock_history('~~test~~', datetime(2000, 1, 1), datetime(2000, 2, 1)), [])
        self.assertEqual(get_stock_history('~~test~~', datetime(2000, 1, 1), datetime(3000, 1, 1)), [day1, day2])

    def test_fetch_current_quote(self):
        from hello.stock_info import _fetch_current_quote
        import hello.stock_info
        with mock.patch.object(hello.stock_info, '_yahoo_query') as yq:
            yq.return_value = {'query': {'results': {'quote': {'Name': 'asdf', 'info': 5}}}}
            self.assertEqual(_fetch_current_quote('asdf'), {'Name': 'asdf', 'info': 5})
            yq.return_value = {'query': {'results': {'quote': {'Name': None, 'info': 5}}}}
            self.assertEqual(_fetch_current_quote('asdf'), {})
            yq.return_value = {}
            self.assertEqual(_fetch_current_quote('asdf'), {})
            yq.return_value = None
            self.assertEqual(_fetch_current_quote('asdf'), {})

    def test_get_current_quote(self):
        from hello.stock_info import get_current_quote, _quotes_cache
        import hello.stock_info
        with mock.patch.object(hello.stock_info, '_fetch_current_quote') as fcq:
            fcq.return_value = {1: 1}
            _quotes_cache.clear()
            gotten = get_current_quote('asdf')
            self.assertEqual(gotten, {1: 1})
            self.assertEqual(_quotes_cache['asdf'][1], {1: 1})
            self.assertEqual(type(_quotes_cache['asdf'][0]), datetime)
            self.assertTrue(get_current_quote('asdf') is gotten)
            # should have been called only once because caching
            self.assertEqual(len(fcq.call_args_list), 1)
            # change it to an expired version in the cache and ensure a refresh
            fcq.return_value = {2: 2}
            _quotes_cache['asdf'] = datetime(1, 1, 1), gotten
            self.assertTrue(get_current_quote('asdf') is fcq.return_value)
            self.assertEqual(len(fcq.call_args_list), 2)

