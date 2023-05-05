import backend.controller as con
import backend.data as data
from backend import queries
import sqlalchemy as alc

class pattern_search:
    xmin, xmax, ymin, ymax = None, None, None, None
    result = None
    status = None

    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = (xmin * data.delta_x) + data.global_x_min
        self.xmax = (xmax * data.delta_x) + data.global_x_min
        self.ymin = (ymin * data.delta_y) + data.global_y_min
        self.ymax = (ymax * data.delta_y) + data.global_y_min

        area_status = self.check_area()

        if area_status == -1:
            self.status = -1
            return
        if area_status == 1:
            self.status = 1
            return

        con.initPItable()
        queries.drop_all_tables()
        con.extract_data(self.xmin, self.ymin, self.xmax, self.ymax);
        con.get_counts_of_each_class()
        con.generate_size_two_tables()
        # max_size = con.check_further(2)
        self.result = []
        self.status = 0
        
        sql = alc.text(
            "INSERT INTO rectangles (name, geog) VALUES ('abc', ST_GeogFromText('POLYGON(({} {}, {} {}, {} {}, {} {}, {} {}))'))"
            .format(self.xmin, self.ymin, self.xmax, self.ymin, 
            self.xmax, self.ymax, self.xmin, self.ymax, self.xmin, self.ymin))
        
        # sql = alc.text(
        #     "INSERT INTO rectangles (name, geog) VALUES ('abc', ST_GeogFromWKB(ST_AsBinary(ST_MakeLine(ST_MakePoint({}, {}), ST_MakePoint({}, {}), ST_MakePoint({}, {}), ST_MakePoint({}, {}), ST_MakePoint({}, {}))), 4326));".format(self.xmin, self.ymin, self.xmax, self.ymin, 
        #     self.xmax, self.ymax, self.xmin, self.ymax, self.xmin, self.ymin)
        # )

        # sql = alc.text(
        #     "INSERT INTO rectangles (name, geog) VALUES ('abc', ST_MakeLine(ST_MakePoint({}, {}), ST_MakePoint({}, {}), ST_MakePoint({}, {}), ST_MakePoint({}, {}), ST_MakePoint({}, {})), 4326)".format(self.xmin, self.ymin, self.xmax, self.ymin, 
        #     self.xmax, self.ymax, self.xmin, self.ymax, self.xmin, self.ymin)
        # )
        
        data.db_conn.execute(sql)
        # print(self.xmin, self.ymin, self.xmax, self.ymax, self.status)
        print(xmin, ymin, xmax, ymax, self.status)
    
    def check_area(self):
        a = con.haversine_distance(self.ymin, self.xmin, self.ymax, self.xmin)
        b = con.haversine_distance(self.ymin, self.xmin, self.ymin, self.xmax)
        area = a * b
        print("area : ", area)
        if area >= data.min_area and area <= data.max_area:
            return 0
        elif area < data.min_area:
            return -1
        elif area > data.max_area:
            return 1