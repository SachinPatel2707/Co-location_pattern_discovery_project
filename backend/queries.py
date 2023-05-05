from sqlalchemy import text
from backend.data import *
import os

create_all_orig_tables_queries = []
create_all_orig_tables_queries.append(text("create table if not exists orig_a (gid serial primary key, longitude varchar(50), latitude varchar(50), geog geography(point));"))
create_all_orig_tables_queries.append(text("create table if not exists orig_b (gid serial primary key, longitude varchar(50), latitude varchar(50), geog geography(point));"))
create_all_orig_tables_queries.append(text("create table if not exists orig_c (gid serial primary key, longitude varchar(50), latitude varchar(50), geog geography(point));"))
create_all_orig_tables_queries.append(text("create table if not exists orig_d (gid serial primary key, longitude varchar(50), latitude varchar(50), geog geography(point));"))
create_all_orig_tables_queries.append(text("create table if not exists orig_e (gid serial primary key, longitude varchar(50), latitude varchar(50), geog geography(point));"))

create_orig_indexes_queries = []
create_orig_indexes_queries.append(text("create index orig_a_idx on orig_a using GIST (geog);"))
create_orig_indexes_queries.append(text("create index orig_b_idx on orig_b using GIST (geog);"))
create_orig_indexes_queries.append(text("create index orig_c_idx on orig_c using GIST (geog);"))
create_orig_indexes_queries.append(text("create index orig_d_idx on orig_d using GIST (geog);"))
create_orig_indexes_queries.append(text("create index orig_e_idx on orig_e using GIST (geog);"))

# create_all_tables_queries = []
# create_all_tables_queries.append(text("create table if not exists a (gid serial primary key, longitude varchar(50), latitude varchar(50), geog geography(point));"))
# create_all_tables_queries.append(text("create table if not exists b (gid serial primary key, longitude varchar(50), latitude varchar(50), geog geography(point));"))
# create_all_tables_queries.append(text("create table if not exists c (gid serial primary key, longitude varchar(50), latitude varchar(50), geog geography(point));"))
# create_all_tables_queries.append(text("create table if not exists d (gid serial primary key, longitude varchar(50), latitude varchar(50), geog geography(point));"))
# create_all_tables_queries.append(text("create table if not exists e (gid serial primary key, longitude varchar(50), latitude varchar(50), geog geography(point));"))

create_indexes_queries = []
create_indexes_queries.append(text("create index a_idx on a using GIST (geog);"))
create_indexes_queries.append(text("create index b_idx on b using GIST (geog);"))
create_indexes_queries.append(text("create index c_idx on c using GIST (geog);"))
create_indexes_queries.append(text("create index d_idx on d using GIST (geog);"))
create_indexes_queries.append(text("create index e_idx on e using GIST (geog);"))

def create_all_tables(isOriginal = False):
    if isOriginal:
        for q in create_all_orig_tables_queries:
            db_conn.execute(q)
        create_indexes(True)
        return
        
    # for q in create_all_tables_queries:
    #     db_conn.execute(q)
    # create_indexes()

def create_indexes(isOriginal = False):
    if isOriginal:
        for q in create_orig_indexes_queries:
            db_conn.execute(q)
        return
        
    for q in create_indexes_queries:
        db_conn.execute(q)

def drop_all_tables(include_originals = False):
    for tables in delete_tables:
        for name in tables:
            db_conn.execute(text("drop table if exists {}".format(name)))

    if include_originals:
        for table in orig_tables:
            db_conn.execute(text("drop table if exists {}".format(table)))

def read_from_single_file():
    path = os.getcwd() + "/data/data_large.csv"
    file = open(path, 'r')
    data = file.readlines()
    write_files = {}
    for table in tables[1]:
        write_files[table] = open(os.getcwd() + "/data/large_dataset/" + table + ".csv", 'w')
    
    for line in data:
        long, lat = line.split(" ")
        # classtype, name, long, lat = line.split(" ")
        # table = name[:1].lower()
        # table = classtype.lower()
        str = "{},{}".format(long, lat)
        write_files[table].write(str)
    
    for table in tables[1]:
        write_files[table].close()     

def load_initial_data():
    # clear_directory(os.getcwd()+"/data/output/")
    # read_from_single_file()
    for table in orig_tables:
        path = os.getcwd() + "/data/data_small/" + table + ".csv"
        # path = os.getcwd() + "/data/large_dataset/" + table + ".csv"
        file = open(path, 'r')
        data = file.readlines()
        for line in data:
            name, long, lat = line.split(",")
            db_conn.execute(text("insert into {} (longitude, latitude, geog) values ({}, {}, 'POINT({} {})')".format(table, long, lat, long, lat)))
        file.close()

def clear_directory(path):
    for file_name in os.listdir(path):
        file = path + file_name
        if os.path.isfile(file):
            os.remove(file)