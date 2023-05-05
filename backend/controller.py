from collections import OrderedDict
import geopandas as gpd
import pandas as pd
from backend import data
from backend.queries import clear_directory
from backend import queries
import sqlalchemy as alc
import os, sys, random, math
import prettytable as pt
import matplotlib.pyplot as plt



def generate_data(size):
    # clear_directory(os.getcwd()+"/data/large_dataset/")
    clear_directory(os.getcwd()+"/data/small_dataset/")
    for name in data.tables[1]:
        # file = open(os.getcwd() + "/data/large_dataset/{}.csv".format(name), 'w')
        file = open(os.getcwd() + "/data/small_dataset/{}.csv".format(name), 'w')
        for i in range(size):
            long = random.uniform(data.gurugram_long, data.meerut_long)
            lat = random.uniform(data.gurugram_lat, data.meerut_lat)
            str = "{},{}\n".format(long, lat)
            file.write(str)
        file.close()

def get_counts_of_each_class():
    for i in range(len(data.tables[1])):
        data.count[data.tables[1][i]] = data.db_conn.execute(alc.text('select count(*) from {}'.format(data.tables[1][i]))).fetchone()[0]

def spatial_join(x, y):
    sql = alc.text("select {}.geog, {}.gid as gid1, {}.gid as gid2 from {} join {} on ST_DWithin({}.geog, {}.geog, {})".format(x, x, y, x, y, x, y, data.dist_h))
    listings = gpd.GeoDataFrame.from_postgis(sql, data.db_conn, geom_col='geog')
    return listings

def fill_size_two_table(col1, col2, _data):
    table_name = col1+col2
    sql = alc.text("create table {} (id serial primary key, {} integer, {} integer)".format(table_name, col1, col2))
    data.db_conn.execute(sql)

    if (_data.shape[0] > 0):
        for i in range(_data.shape[0]):
            sql = alc.text("insert into {} ({}, {}) values ({}, {})".format(table_name, col1, col2, _data['gid1'][i], _data['gid2'][i]))
            data.db_conn.execute(sql)

def generate_size_two_tables():
    new_tables = []
    for i in range(len(data.tables[1])):
        for j in range(i+1, len(data.tables[1])):
            join_res = spatial_join(data.tables[1][i], data.tables[1][j])
            col1 = data.tables[1][i]
            col2 = data.tables[1][j]
            new_tables.append(col1+col2) 
            fill_size_two_table(col1, col2, join_res)
    data.tables.append(new_tables)
    verify_PI(2)

def verify_PI(size):
    temp_table = [t for t in data.tables[size]]
    for t in temp_table:
        sql = alc.text("select count(*) from {}".format(t));
        pattern_count = data.db_conn.execute(sql).fetchone()[0]
        # print(t, " occurs ", pattern_count)
        cols = [x for x in t]
        # cur_count = {}
        # for i in range(len(t)):
        #     cur_count[t[i]] = db_conn.execute(alc.text("select count(distinct {}) from {}".format(cols[i], t))).fetchone()[0]
        cur_PI = getPI(cols, pattern_count)
        # print(cur_PI)
        data.PI_of_tables[t] = cur_PI
        if (cur_PI < data.PI):
            data.db_conn.execute(alc.text('drop table {}'.format(t)))
            data.tables[size].remove(t)
        else:
            data.patterns_found.add(t)

# def getPI(cols, cur_count):
#     min_pr = 10
#     for col in cols:
#         pr = cur_count[col]/count[col]
#         min_pr = min(min_pr, pr)
#     return min_pr

def getPI(cols, cur_count):
    pr = 1
    for col in cols:
        pr = pr * data.count[col]
    return cur_count / pr if pr != 0 else 0

def check_further(size):
    if (len(data.tables[size]) > 0):
        new_tables = []
        for i in range(len(data.tables[size])):
            for j in range(i+1, len(data.tables[size])):
                # print("i = {} and j = {}".format(i, j))  # LOG
                mp = {}
                table_col_mapping = {}
                t1 = data.tables[size][i]
                t2 = data.tables[size][j]
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
                    
        data.tables.append(new_tables)
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
    data.db_conn.execute(sql)

def verify_neighbourhood(table_name, keys, verify_table, cols):
    size = len(verify_table)
    if verify_table in data.tables[size]:
        # delete from abc where not exists (select * from bc where bc.b = abc.b and bc.c = abc.c);
        sql = "delete from {} where not exists (select * from {} where ".format(table_name, verify_table)
        for col in cols:
            sql += "{}.{} = {}.{} and ".format(table_name, col, verify_table, col)
        sql = sql[: len(sql)-5]
        sql += ")"
        # print(sql) # LOG
        data.db_conn.execute(alc.text(sql))
    else:
        # if bc itself failed to cross the threshold then, abc combination is impossible to make
        # hence, just drop this whole abc table
        sql = "drop table {}".format(table_name)
        data.db_conn.execute(alc.text(sql))
        return True
    return False

def print_table(size):
    final_res = []
    table_names = []
    pi = []
    maxlen = 0
    for name in data.tables[size]:
        pi.append("PI : {}".format(data.PI_of_tables[name]))
        res = data.db_conn.execute(alc.text("select * from {}".format(name)))
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
    for table in data.tables[1]:
        data.PI_of_tables[table] = 1.0


#############     for Project     ###############

def minimum_bounding_rectangle(points):
    # Find the minimum and maximum x and y coordinates of the points.
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)

    # Return the coordinates of the minimum bounding rectangle.
    return [(min_x, min_y), (max_x, max_y)]

def find_area_of_rectangle(y_max, x_max, y_min, x_min):
    # compute the distance between the two corners along the latitude and longitude
    R = 6371  # radius of the earth in kilometers
    dLat = math.radians(y_max - y_min)
    dLon = math.radians(x_max - x_min)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(y_min)) * math.cos(math.radians(y_max)) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    length = R * c  # length of the rectangle in kilometers
    # width of the rectangle in kilometers
    width = R * c * math.cos(math.radians((y_min + y_max) / 2))

    # convert the length and width to square kilometers
    # length_km2 = length * length
    # width_km2 = width * width

    # compute the area of the rectangle in square kilometers
    # area = length_km2 * width_km2
    area = length * width

    print("The area of the rectangle is: {:.2f} square kilometers".format(area))
    print("length: {} \t breadth: {}".format(length, width))


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Compute the Haversine distance between two points given their latitude and longitude coordinates.
    """
    R = 6371  # radius of the earth in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def visualise_grid():
    x, y = data.grid_x, data.grid_y
    fig, ax = plt.subplots()

    ax.vlines(x=x, ymin=min(y), ymax=max(y), color='gray', linestyle='dashed')
    ax.hlines(y=y, xmin=min(x), xmax=max(x), color='gray', linestyle='dashed')

    # for i in range(len(x)):
    #     for j in range(len(y)):
    #         rect = plt.Rectangle((x[i], y[j]), delta_x, delta_y, fill=None, edgecolor='red', lw=2)
    #         ax.add_patch(rect)
    #         # ax.set_xlim(min(x), max(x))
    #         # ax.set_ylim(min(y), max(y))
    #         plt.pause(0.2)
    #         rect.remove()

    plt.show()

def extract_data(xmin, ymin, xmax, ymax):
    for i in range(len(data.tables[1])):
        sql = alc.text("Create table {} as select * from {} where cast (latitude as double precision) between {} and {} and cast (longitude as double precision) between {} and {}".format(data.tables[1][i], data.orig_tables[i], ymin, ymax, xmin, xmax))
        data.db_conn.execute(sql)
    queries.create_indexes()