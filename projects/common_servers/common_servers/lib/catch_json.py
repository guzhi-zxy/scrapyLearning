# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: catch_json.py
@time: 2020-10-27 14:50:59
@projectExplain: 
"""

import json

from datetime import datetime
from decimal import Decimal
from functools import singledispatch


class MyEncoder:
    def __init__(self, value):
        self._value = value

    def get_value(self):
        return self._value


@singledispatch
def convert(o):
    raise TypeError('can not convert type')


@convert.register(set)
def _(o):
    return list(o)


@convert.register(datetime)
def _(o):
    return o.strftime('%Y-%m-%d %H:%M:%S')


@convert.register(Decimal)
def _(o):
    return float(o)


@convert.register(MyEncoder)
def _(o):
    return o.get_value()


class ExtendJSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time, decimal types, and
    UUIDs.
    """

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        try:
            return convert(o)
        except TypeError:
            return super(ExtendJSONEncoder, self).default(o)


if __name__ == "__main__":
    a = {"a": {1, 23}}
    b = json.dumps(a, cls=ExtendJSONEncoder)
    print(b)
