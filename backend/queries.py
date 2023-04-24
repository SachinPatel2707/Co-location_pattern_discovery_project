from sqlalchemy import text
from backend.data import *
import os

create_all_tables_queries = []
create_all_tables_queries.append(text("create table if not exists a (gid serial primary key, longitude varchar(50), latitude varchar(50), geog geography(point));"))
create_all_tables_queries.append(text("create table if not exists b (gid serial primary key, longitude varchar(50), latitude varchar(50), geog geography(point));"))
create_all_tables_queries.append(text("create table if not exists c (gid serial primary key, longitude varchar(50), latitude varchar(50), geog geography(point));"))
create_all_tables_queries.append(text("create table if not exists d (gid serial primary key, longitude varchar(50), latitude varchar(50), geog geography(point));"))
create_all_tables_queries.append(text("create table if not exists e (gid serial primary key, longitude varchar(50), latitude varchar(50), geog geography(point));"))

create_indexes_queries = []
create_indexes_queries.append(text("create index a_idx on a using GIST (geog);"))
create_indexes_queries.append(text("create index b_idx on b using GIST (geog);"))
create_indexes_queries.append(text("create index c_idx on c using GIST (geog);"))
create_indexes_queries.append(text("create index d_idx on d using GIST (geog);"))
create_indexes_queries.append(text("create index e_idx on e using GIST (geog);"))

def create_all_tables():
    for q in create_all_tables_queries:
        db_conn.execute(q)
    create_indexes()

def create_indexes():
    for q in create_indexes_queries:
        db_conn.execute(q)

def drop_all_tables():
    for tables in delete_tables:
        for name in tables:
            db_conn.execute(text("drop table if exists {}".format(name)))

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
    clear_directory(os.getcwd()+"/data/output/")
    # read_from_single_file()
    for table in tables[1]:
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