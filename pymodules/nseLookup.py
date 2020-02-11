#!/usr/bin/env python

import requests
import pygal
import math
from re import findall
from bs4 import BeautifulSoup
from datetime import datetime


class parser(object):
    session = requests.Session()
    cookies =  None
    session.headers = { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", "Connection": "keep-alive" }

    def __init__(self, url):
        self.url = url


    def get(self, url):
        o = parser.session.get(url)
        parser.cookies = o.cookies
        parser.session.headers = o.request.headers
        return o

    def parse(self):
        data = self.get("https://www1.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbol="+self.url)
        try:
            if data.status_code ==  200:
                html = data.text
                header =  self.getHeader(html)
                table = self.getTable(html)
                info = " ".join(table[0]).split(":", 1)[1]
                strike_price = self.packer(header, table)
                marker, offset = self.marker_value(table)
                format = {"name": self.url, "option-chain": strike_price, "marker": marker, "offset": offset, "info": "Value for " + info}
                # limited = self.prepare_present(format)
                # return limited
                return format
            else:
                return None
        except :
            return None

    def Stocks(self):
        data = self.get("https://www1.nseindia.com/products/content/derivatives/equities/fo_underlyinglist.htm")
        try:
            if data.status_code == 200:
                html = data.text
                stks = self.getTable(html)
                return stks
            else:
                return None
        except Exception as e:
            print "Exception" + str(e)
            return None

    def marker_value(self, data):
        getValue = data[0][1]
        value = findall("\d+\.\d+", getValue)
        cur_value =  (value and value or findall("\d+", getValue))
        round_value = lambda num, offset: float(math.ceil(num / offset) * offset)
        if float(cur_value[0]) > 15000 and float(cur_value[0]) < 30000:
            return round_value(float(cur_value[0]), 100), 100
        elif float(cur_value[0]) > 1000 and float(cur_value[0]) < 15000:
            return round_value(float(cur_value[0]), 50), 50
        elif float(cur_value[0]) > 100 and float(cur_value[0]) < 1000:
            return round_value(float(cur_value[0]), 10), 10
        else:
            return round_value(float(cur_value[0]), 5), 5



    def packer(self, header, table):
        tbl = {}
        call_header = header[1][0:11]
        put_header = header[1][12:]
        for i in table:
            if len(i) == 23:
      #          t = isinstance(datetime.strptime(i[11], datetime), datetime) and i[11] or float(i[11]) 
                tbl[float(i[11])] = {"call": dict(zip(call_header, i[0:11])), "put": dict(zip(put_header, i[12:]))}
            else:
                pass
        return tbl

    def getHeader(self, data):
        table_data = [[cell.text for cell in row("th")] for row in BeautifulSoup(data, features="lxml")("tr")]
        cleaned = self._cleaner(table_data)
        return cleaned

    def getTable(self, data):
            table_data = [[cell.text for cell in row("td")] for row in BeautifulSoup(data, features="lxml")("tr")]
            cleaned = self._cleaner(table_data)
            return cleaned

    def _cleaner(self, data):
        out = []
        for i in data:
            if len(i) > 1:
                f = map(lambda x: x.strip().encode("ascii", "ignore"), i)
                out.append(f)
        return out


    def get_underlying_data(self, price):
	tbl = []
	date = datetime.now()
        p = "%.2f" %round(price)
        instrument = self.url in ["NIFTY", "BANKNIFTY", "NIFTYIT"] and "OPTIDX" or "OPTSTK" 
        url = "https://www1.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionDates.jsp?symbol="+self.url+"&instrument="+ instrument +"&strike=" + str(p)
        data  = self.get(url)
        if data.status_code == 200:
            html = data.text
            header = self.getHeader(html)
            table = self.getTable(html)
	    for i in table[1:]:
	        if len(i) == 23 and datetime.strptime(i[11], "%d%b%Y").month - date.month < 2:
	            tmp = {}
	            tmp[i[11]] = {"call": dict(zip(header[1][1:11], i[1:11])), "put":dict(zip(header[1][12:-1:], i[12:-1:]))}
	            tbl.append(tmp)
        return tbl


###################################################################################

class MapFormat(parser):
    def __init__(self, offset=1, url="NIFTY"):
        self.offset = offset
        self.url = url
        parser.__init__(self, url= url)

    def prepare_present(self):
        data = self.parse()
        new_data = {}
        table = data["option-chain"]
        offset = data["offset"]
        marker = data["marker"]
        inc = marker
        new_data[marker] = table[marker]
        for i in range(0, self.offset):
            inc = inc  + offset
            if inc in table:
                new_data[inc] =  table[inc]
            else:
                break
        inc = marker
        for i in range(0, self.offset):
            inc = inc  - offset
            if inc in table:
                new_data[inc] =  table[inc]
            else:
                break
        final_data = {"tables" : new_data}
        final_data["name"] = data["name"]
        final_data["current_strike-price"] = data["marker"]
        final_data["info"] = data["info"]
        return final_data

    def __replace__(self, x):
        if x in ['', '-']:
            return None
        elif not x:
            return 0
        else:
            return int(x.replace(',', ''))

    def __sumtotal__(self, list1, list2):
        total = 0
        for i, v in enumerate(list1):
            out = list1[i] * list2[i]
            total = out + total
        return total

    def oi_change_graph(self):
        data = self.prepare_present()
        graph = {
            "str_price": None,
            "puts": None,
            "calls": None
        }
        str_price = sorted(data['tables'].keys())
        puts = map(self.__replace__, [data['tables'][i]['put']['Chng in OI']  for i in str_price])
        calls = map(self.__replace__, [data['tables'][i]['call']['Chng in OI'] for i in str_price])
        graph["str_price"] = map(str, map(int, str_price))
        graph["puts"] = puts
        graph["calls"] = calls

        line_chart = pygal.Bar(legend_at_bottom=True, legend_at_bottom_columns=4)
        line_chart.title = 'Change in OI for ' + data["name"]
        line_chart.x_labels = map(str, map(int, str_price))
        line_chart.add('Chg puts OI', puts)
        line_chart.add('Chg calls OI', calls)
        line_chart.render()
        graph_data = line_chart.render_data_uri()
        return graph_data, graph


    def oi_numbers(self):
        data = self.prepare_present()
        graph = {
            "str_price": None,
            "puts": None,
            "calls": None
        }

        str_price = sorted(data['tables'].keys())
        puts = map(self.__replace__, [data['tables'][i]['put']['OI']  for i in str_price])
        calls = map(self.__replace__, [data['tables'][i]['call']['OI'] for i in str_price])
        graph["str_price"] = map(str, map(int, str_price))
        graph["puts"] = puts
        graph["calls"] = calls

        line_chart = pygal.Bar(legend_at_bottom=True, legend_at_bottom_columns=4)
        line_chart.title = 'OI EOD for ' + data["name"]
        line_chart.x_labels = map(str, map(int, str_price))
        line_chart.add('Puts OI', puts)
        line_chart.add  ('Calls OI', calls)
        line_chart.render()
        graph_data = line_chart.render_data_uri()
        return graph_data, graph


    def max_pain(self):
        str_price = []
        max_pain = []
        data = self.prepare_present()
        keys = sorted(data['tables'].keys())
        putval = [0 if not i else i  for i in map(self.__replace__, [data["tables"][i]["put"]["OI"] for i in keys])]
        callval = [0 if not i else i for i in map(self.__replace__, [data["tables"][i]["call"]["OI"] for i in keys])]
        for k, i in enumerate(keys):
            call_v = i *  sum(callval[0:k+1:]) - self.__sumtotal__(callval[0:k+1:], keys[0:k+1:])
            put_v =  self.__sumtotal__(keys[k::], putval[k::]) - i *  sum(putval[k::])
            str_price.append(i)
            max_pain.append(call_v + put_v)

        line_chart = pygal.Bar(legend_at_bottom=True, legend_at_bottom_columns=4)
        line_chart.title = 'Max pain graph for ' + data["name"]
        line_chart.x_labels = map(str, str_price)
        line_chart.add(None, max_pain)
        line_chart.render()
        graph_data = line_chart.render_data_uri()
        return graph_data

    def all_stats(self):
       dump = {}
       data = self.prepare_present()
       for d in sorted(data["tables"].keys()):
           get_minute = self.get_underlying_data(d)
           dump[d] = get_minute
       return dump


