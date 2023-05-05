import backend
import sys, os, time
from backend import data
from backend import grid_search as gs

# backend.generate_data(100)
# backend.initPItable()
# backend.drop_all_tables(include_originals = True)
# backend.create_all_tables(isOriginal = True)
# backend.load_initial_data()
# backend.get_counts_of_each_class()
# backend.generate_size_two_tables()
# max_size = backend.check_further(2)

# print("\nBiggest co-relation found among the 5 classes is of size {}".format(max_size))
# for t in tables[max_size]:
#     print("PI of {} : {}".format(t, PI_of_tables[t]))

# for i in range(1, max_size+1):
#     with open(os.getcwd() + "/data/output/size_{}.txt".format(i), 'w') as sys.stdout:
#         backend.print_table(i)

start = time.time()
grid = gs.Grid()
grid.iterate()
end = time.time()

with open('data/output/output3.txt', 'w') as f:
    print('distance : ', data.dist_h, file=f)
    print('threshold : ', data.PI, file=f)
    print('no. of rows : ', data.y_lambda, file=f)
    print('no. of columns : ', data.x_lambda, file=f)

    print("total rectangles : ", data.total_rects, file=f)
    print("rectangles with patterns : ", data.rects_with_patterns, file=f)
    print("\n")
    for res in data.final_res:
        print(res, file=f)

    print("\n\nExecution Time in seconds : ", end-start, file=f)