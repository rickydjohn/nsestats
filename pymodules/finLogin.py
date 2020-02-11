#!/usr/bin/env python

import MySQLdb
import hashlib


class Connector():
    def __init__(self, host, username, password, database):
        self.host = host
        self.username = username
        self.password = password
        self.database = database

    def mysqlObject(self):
        conn = MySQLdb.Connect(self.host, self.username, self.password, self.database)
        curs = conn.cursor()
        return conn, curs

    def checkLogin(self, username, password):
        data = {"f_name": "",
                "email": "",
                "state": "",
                "Authenticated": False
                }
        check_pass = lambda x: hashlib.md5(x).hexdigest()
        check_username = "select a.f_name, a.password, b.state, b.created_at from " \
                         "users a join user_state b on a.id=b.id and b.version=(select max(version) from user_state where id=a.id) " \
                         "where a.email='"+ username +"' and  a.password=md5('"+ password  +"') and b.state !='deleted'"
        conn, curs = self.mysqlObject()
        curs.execute(check_username)
        if curs.rowcount == 0:
            return data
        else:
            sql_out = curs.fetchall()
            conn.close()
            if check_pass(password) == sql_out[0][1]:
                data["f_name"] = sql_out[0][0]
                data["email"] = username
                data["Authenticated"] = True
                data["state"] = sql_out[0][2]
                print data
                return data

    def get_user(self, user):
        user_data = {
            "f_name" : "",
            "l_name": "",
            "email": "",
        }
        conn, curs = self.mysqlObject()
        user_details = "select f_name, l_name, email, password from users WHERE email='"+user+"';"
        curs.execute(user_details)
        data = curs.fetchall()
