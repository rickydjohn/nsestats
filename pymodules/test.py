#!/usr/bin/env python


from nseLookup import MapFormat, parser
import json

call = "call"
a =  MapFormat(offset=3, url="NIFTY")
o = a.prepare_present()
print a.cookies
#so = sorted(o["tables"].keys())
#print"%-15s %-15s %-15s %-10s %-10s %-10s %-10s" %("Strike Price", "OI", "Change in OI", "Net Chng", "Volume", "IV", "Bid Price")
#for i in so:
#    p = a.get_underlying_data(i)
#    print "-" * 85
#    print i
#    print "-" * 85
#    for j in p:
#        k = j.keys()[0]
#        print "%-15s %-15s %-15s %-10s %-10s %-10s %-10s" %(k, j[k][call]["OI"], j[k][call]["Chng in OI"], j[k][call]["Net Chng"], j[k][call]["Volume"],j[k][call]["IV"],j[k][call]["BidPrice"])
#    
