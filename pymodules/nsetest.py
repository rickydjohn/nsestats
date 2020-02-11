#!/usr/bin/python

from nseLookup import parser

a = parser("NIFTY")
print a.Stocks()
print a.parse()
