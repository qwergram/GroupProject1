# coding=utf-8
import os


def load_data(filename):
    with open(os.path.join("hello", "testdata", filename), 'r', encoding='utf-8') as f:
        return f.read()
