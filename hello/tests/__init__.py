# coding=utf-8
from __future__ import unicode_literals
from builtins import open
import os


def load_data(filename):
    with open(os.path.join("hello", "testdata", filename), 'r', encoding='utf-8') as f:
        return f.read()
