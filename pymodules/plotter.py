#!/usr/bin/python

import MySQLdb
import datetime
import math


def db_conn():
    db = MySQLdb.connect("localhost", "root", "megh", "fintech")
    curs = db.cursor()
    return db, curs


def marker_value(data):
    cur_value =  data
    round_value = lambda num, offset: float(math.ceil(num / offset) * offset)
    if float(cur_value[0]) > 15000 and float(cur_value[0]) < 30000:
        return round_value(float(cur_value[0]), 100)
    elif float(cur_value[0]) > 1000 and float(cur_value[0]) < 15000:
        return round_value(float(cur_value[0]), 50)
    elif float(cur_value[0]) > 100 and float(cur_value[0]) < 1000:
        return round_value(float(cur_value[0]), 10)
    else:
        return round_value(float(cur_value[0]), 5)

def query_curtime(data,share):
    db, curs = db_conn()
    str_price = marker_value(data)
    created_at = datetime.datetime.strftime(data[1], "%Y-%m-%d %H:%M:%S")
    quer = 'select call_type,cur_price,strike_price,OI,Chng_in_OI,Volume,IV,LTP,Net_Chng,BidQty,BidPrice,AskPrice,AskQty ' \
           'from shares a join oi_change b on a.id=b.share where ' \
           'a.name="%s" and b.strike_price=%d and b.created_at="%s"' %(share, str_price, created_at)
    curs.execute(quer)
    out = curs.fetchall()
    header = ["call_type","cur_price","strike_price","OI","Chng_in_OI","Volume","IV","LTP","Net_Chng","BidQty","BidPrice","AskPrice","AskQty"]
    ret_data = {}
    ret_data["strike_price"] = str_price
    ret_data["created_at"] = created_at
    for i in out:
        appen_data = dict(zip(header, i))
        appen_data.pop("strike_price")
        if appen_data["call_type"] == "call":
            ret_data["call"] = appen_data
        elif appen_data["call_type"] == "put":
            ret_data["put"] = appen_data
    db.close()
    return ret_data


def get_pointer(share):
    db, curs =  db_conn()
    quer = "select distinct(b.cur_price), b.created_at from shares a join oi_change b on a.id=b.share where a.name=(\'%s')" %(share)
    curs.execute(quer)
    data = curs.fetchall()
    db.close()
    return data

def get_data(share):
    plt = []
    data = get_pointer(share)
    for i in data:
        plt.append(query_curtime(i, share))
    return plt
