# coding=utf-8
from django.test import TestCase
import os


class StockInfoCase(TestCase):
    def yahoo_data(self):
        with open(os.path.join("hello", "testdata", "yahoo_data.htmlfragment"), 'r', encoding='utf-8') as f:
            return f.read()

    def test_yahoo_data(self):
        from hello.stock_info import _yahoo_top_movers, TopMover
        import hello.stock_info
        hello.stock_info._yahoo_cached = None  # ensure cache is cleared
        data = self.yahoo_data()
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
        # make sure it is caching
        self.assertTrue(_yahoo_top_movers(data) is movers)