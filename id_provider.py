import os
import sqlite3
import csconfig
import time
import random
import sys

databasefile = os.path.join(csconfig.CSServerConfig.db_path, 'ids.db')


def get_table_name():
    return "fileids"


def check_table_existance():
    sql = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s'" % get_table_name()
    conn = sqlite3.connect(databasefile)
    cur = conn.execute(sql)
    ret = int((cur.fetchone()[0]))
    if ret == 0:
        sql = "create table if not exists %s (file_id text, file_name text)" % get_table_name()
        conn.execute(sql)
        conn.commit()
    conn.close()
    return True


def get_id_for_book(file_name):
    fname = csconfig.CSServerConfig.get_relative_path(file_name)
    conn = sqlite3.connect(databasefile)
    sql = "select file_id from %s where file_name = ?" % get_table_name()
    p = (fname,)
    cur = conn.execute(sql, p)
    res = cur.fetchone()
    conn.close()
    if res:
        return res[0]
    return "0"

def add_new_id(file_id, file_name):
    conn = sqlite3.connect(databasefile)
    sql = "insert into %s values (?,?)" % (get_table_name())
    p = (file_id, file_name)
    conn.execute(sql, p)
    conn.commit()
    conn.close()


def get_or_create_id_for_book(file_name):
    fname = csconfig.CSServerConfig.get_relative_path(file_name)
    print fname
    file_id = get_id_for_book(fname)
    if len(file_id) < 5:
        file_id = str(time.time()).replace('.','') + '%02d' % random.randint(1,99)
        add_new_id(file_id, fname)
    return file_id

def main(argv):
    conn = sqlite3.connect(databasefile)
    sql = "select * from %s" % get_table_name()
    cur = conn.execute(sql)
    for item in cur:
        print item

check_table_existance()

if __name__ == "__main__":
    main(sys.argv[1:])