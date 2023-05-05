from backend import data
from backend import controller as con
from backend.pattern_search import pattern_search as PS
import sqlalchemy as alc

class Grid :
    grid_x = None
    grid_y = None
    delta_x = None
    delta_y = None
    delta_area = None

    def __init__(self):
        self.initialise_grid()

    def initialise_grid(self):
        """
        a--------b
        |        |
        |        |
        c--------d

        where c is gurugram and b is meerut
        """

        # distance between c and d
        study_area_x = con.haversine_distance(data.gurugram_lat, data.gurugram_long, data.gurugram_lat, data.meerut_long)

        # distance between c and a
        study_area_y = con.haversine_distance(data.gurugram_lat, data.gurugram_long, data.meerut_lat, data.gurugram_long)

        delta_x = abs(data.gurugram_long - data.meerut_long) / (data.x_lambda * 1.0)
        delta_y = abs(data.gurugram_lat - data.meerut_lat) / (data.y_lambda * 1.0)

        delta_area = (study_area_x / (data.x_lambda * 1.0)) * (study_area_y / (data.y_lambda * 1.0))

        init_x = data.global_x_min
        grid_x = [init_x + k*delta_x for k in range(data.x_lambda)]
        init_y = data.global_y_min
        grid_y = [init_y + k*delta_y for k in range(data.y_lambda)]

        print(delta_x, delta_y, delta_area)
        data.delta_x = delta_x
        data.delta_y = delta_y
        data.delta_area = delta_area
        data.grid_x = grid_x
        data.grid_y = grid_y

    # def iterate(self):
    #     for j in range(len(self.grid_y)):
    #         for i in range(len(self.grid_x)):
    #             xmin, xmax, ymin, ymax = i, i+1, j, j+1
    #             ps = PS(xmin, xmax, ymin, ymax)

    def iterate(self):
        sql = alc.text("delete from rectangles")
        data.db_conn.execute(sql)
        for j in range(data.y_lambda):
            for i in range(data.x_lambda):
                self.solve(i, j, i+1, j+1)
                

    def solve(self, xmin, ymin, xmax, ymax):
        id = str(xmin) + str(ymin) + str(xmax) + str(ymax)
        if id in data.visited:
            return
        data.visited.add(id)

        ps = PS(xmin, ymin, xmax, ymax)
        if ps.status == -1:
            if xmax+1 <= data.x_lambda:
                self.solve(xmin, ymin, xmax+1, ymax)
            if ymax+1 <= data.y_lambda:
                self.solve(xmin, ymin, xmax, ymax+1)
        
        if ps.result != None:
            t = {'coordinates': [[xmin, ymin], [xmax, ymax]],
                'patterns': ps.result}
            data.final_res.append(t)
            data.rects_with_patterns = data.rects_with_patterns + 1
        data.total_rects = data.total_rects + 1

                