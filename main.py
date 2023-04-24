import backend
import sys, os
from backend.data import *

# backend.generate_data(100)
backend.initPItable()
backend.drop_all_tables()
backend.create_all_tables()
backend.load_initial_data()
backend.get_counts_of_each_class()
backend.generate_size_two_tables()
max_size = backend.check_further(2)

print("\nBiggest co-relation found among the 5 classes is of size {}".format(max_size))
for t in tables[max_size]:
    print("PI of {} : {}".format(t, PI_of_tables[t]))

for i in range(1, max_size+1):
    with open(os.getcwd() + "/data/output/size_{}.txt".format(i), 'w') as sys.stdout:
        backend.print_table(i)