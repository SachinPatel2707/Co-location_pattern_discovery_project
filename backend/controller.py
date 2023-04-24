from collections import OrderedDict
import geopandas as gpd
import pandas as pd
from backend.data import *
from backend.queries import clear_directory
import sqlalchemy as alc
import os, sys, random
import prettytable as pt

def generate_data(size):
    # clear_directory(os.getcwd()+"/data/large_dataset/")
    clear_directory(os.getcwd()+"/data/small_dataset/")
    for name in tables[1]:
        # file = open(os.getcwd() + "/data/large_dataset/{}.csv".format(name), 'w')
        file = open(os.getcwd() + "/data/small_dataset/{}.csv".format(name), 'w')
        for i in range(size):
            long = random.uniform(gurugram_long, meerut_long)
            lat = random.uniform(gurugram_lat, meerut_lat)
            str = "{},{}\n".format(long, lat)
            file.write(str)
        file.close()

def get_counts_of_each_class():
    for i in range(len(tables[1])):
        count[tables[1][i]] = db_conn.execute(text('select count(*) from {}'.format(tables[1][i]))).fetchone()[0]

def spatial_join(x, y):
    sql = alc.text("select {}.geog, {}.gid as gid1, {}.gid as gid2 from {} join {} on ST_DWithin({}.geog, {}.geog, {})".format(x, x, y, x, y, x, y, dist_h))
    listings = gpd.GeoDataFrame.from_postgis(sql, db_conn, geom_col='geog')
    return listings

def fill_size_two_table(col1, col2, data):
    table_name = col1+col2
    sql = alc.text("create table {} (id serial primary key, {} integer, {} integer)".format(table_name, col1, col2))
    db_conn.execute(sql)

    if (data.shape[0] > 0):
        for i in range(data.shape[0]):
            sql = alc.text("insert into {} ({}, {}) values ({}, {})".format(table_name, col1, col2, data['gid1'][i], data['gid2'][i]))
            db_conn.execute(sql)

def generate_size_two_tables():
    new_tables = []
    for i in range(len(tables[1])):
        for j in range(i+1, len(tables[1])):
            join_res = spatial_join(tables[1][i], tables[1][j])
            col1 = tables[1][i]
            col2 = tables[1][j]
            new_tables.append(col1+col2) 
            fill_size_two_table(col1, col2, join_res)
    tables.append(new_tables)
    verify_PI(2)

def verify_PI(size):
    temp_table = [t for t in tables[size]]
    for t in temp_table:
        cols = [x for x in t]
        cur_count = {}
        for i in range(len(t)):
            cur_count[t[i]] = db_conn.execute(alc.text("select count(distinct {}) from {}".format(cols[i], t))).fetchone()[0]
        cur_PI = getPI(cols, cur_count)
        # print(cur_PI)
        PI_of_tables[t] = cur_PI
        if (cur_PI < PI):
            db_conn.execute(text('drop table {}'.format(t)))
            tables[size].remove(t)

def getPI(cols, cur_count):
    min_pr = 10
    for col in cols:
        pr = cur_count[col]/count[col]
        min_pr = min(min_pr, pr)
    return min_pr

def check_further(size):
    if (len(tables[size]) > 0):
        new_tables = []
        for i in range(len(tables[size])):
            for j in range(i+1, len(tables[size])):
                # print("i = {} and j = {}".format(i, j))  # LOG
                mp = {}
                table_col_mapping = {}
                t1 = tables[size][i]
                t2 = tables[size][j]
                for k in t1:
                    mp[k] = (mp[k]+1) if k in mp.keys() else 1
                    if k not in table_col_mapping.keys():
                        table_col_mapping[k] = t1 
                for k in t2:
                    mp[k] = (mp[k]+1) if k in mp.keys() else 1
                    if k not in table_col_mapping.keys():
                        table_col_mapping[k] = t2
                mp = OrderedDict(sorted(mp.items()))
                keys = list(mp.keys())
                common_cols = [k for k in keys if mp[k] > 1]
                dist_cols = [k for k in keys if mp[k] == 1]
                
                table_name = ""
                for k in keys:
                    table_name += k
                
                table_to_verify_neighbourhood = ""
                for k in dist_cols:
                    table_to_verify_neighbourhood += k
                
                if table_name not in new_tables and len(dist_cols) == 2 and len(dist_cols)+len(common_cols) == len(keys):
                    new_tables.append(table_name)
                    create_next_table(table_name, common_cols, table_col_mapping, t1, t2)
                    isRemoved = verify_neighbourhood(table_name, keys, table_to_verify_neighbourhood, dist_cols)
                    if isRemoved == True:
                        new_tables.remove(table_name)
                    
        tables.append(new_tables)
        verify_PI(size+1)
        return check_further(size+1)
    else:
        return size-1

def create_next_table(name, common_cols, table_col_mapping, t1, t2):
    # create table abc as select ab.a as a, ab.b as b, bc.c as c from ab join bc on ab.b = bc.b;
    sql = "create table if not exists {} as select ".format(name)
    for col, tab in table_col_mapping.items():
        sql += "{}.{} as {}, ".format(tab, col, col)
    sql = sql[: len(sql)-2]
    sql += " from {} join {} on ".format(t1, t2)

    for col in common_cols:
        sql += "{}.{} = {}.{} and ".format(t1, col, t2, col)
    
    sql = sql[: len(sql)-5]
    # print(sql) # LOG
    sql = alc.text(sql)
    db_conn.execute(sql)

def verify_neighbourhood(table_name, keys, verify_table, cols):
    size = len(verify_table)
    if verify_table in tables[size]:
        # delete from abc where not exists (select * from bc where bc.b = abc.b and bc.c = abc.c);
        sql = "delete from {} where not exists (select * from {} where ".format(table_name, verify_table)
        for col in cols:
            sql += "{}.{} = {}.{} and ".format(table_name, col, verify_table, col)
        sql = sql[: len(sql)-5]
        sql += ")"
        # print(sql) # LOG
        db_conn.execute(alc.text(sql))
    else:
        # if bc itself failed to cross the threshold then, abc combination is impossible to make
        # hence, just drop this whole abc table
        sql = "drop table {}".format(table_name)
        db_conn.execute(alc.text(sql))
        return True
    return False

def print_table(size):
    final_res = []
    table_names = []
    pi = []
    maxlen = 0
    for name in tables[size]:
        pi.append("PI : {}".format(PI_of_tables[name]))
        res = db_conn.execute(alc.text("select * from {}".format(name)))
        res = res.fetchall()
        
        cols = [k for k in name]
        table_name = ""
        for col in cols:
            table_name += (col+"-")
        table_name = table_name[:len(table_name)-1]
        table_names.append(table_name)

        format_res = []
        for r in res:
            temp = ""
            for i in range(len(cols)):
                temp += "{}{}-".format(cols[i], r[i])
            temp = temp[: len(temp)-1]
            format_res.append(temp)
        format_res.append("")
        final_res.append(format_res)
        maxlen = max(maxlen, len(format_res))
    
    # add padding to each column to make them of equal length
    for res in final_res:
        if len(res) < maxlen:
            res += ['']*(maxlen - len(res))

    res = pt.PrettyTable()
    
    for i in range(len(table_names)):
        res.add_column(table_names[i], final_res[i])
    
    res.add_row(pi)
    print(res)

def initPItable():
    for table in tables[1]:
        PI_of_tables[table] = 1.0


#############     for Project     ###############

def minimum_bounding_rectangle(points):
    # Find the minimum and maximum x and y coordinates of the points.
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)

    # Return the coordinates of the minimum bounding rectangle.
    return [(min_x, min_y), (max_x, max_y)]
