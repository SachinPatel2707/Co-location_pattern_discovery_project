from backend.db_connection import connect_to_db
from sqlalchemy import text

dist_h = 12000
PI = 0.3
# global_x_min = gurugram_long = 77.026344
# global_y_min = gurugram_lat = 28.457523
# global_x_max = meerut_long = 77.705956
# global_y_max = meerut_lat = 28.984644

global_x_min = gurugram_long = 76.97
global_y_min = gurugram_lat = 28.43
global_x_max = meerut_long = 77.705956
global_y_max = meerut_lat = 28.984644

db_conn = connect_to_db()

orig_tables = ['orig_a', 'orig_b', 'orig_c', 'orig_d', 'orig_e']
tables = [[], ['a', 'b', 'c', 'd', 'e']]
# tables = [[], ['a', 'b', 'c']]

delete_tables = [['a', 'b', 'c', 'd', 'e'], ['ab', 'ac', 'ad', 'ae', 'bc', 'bd', 'be', 'cd', 'ce', 'de'], ['abc', 'abd', 'abe', 'acd', 'ace', 'ade', 'bcd', 'bce', 'bde', 'cde'], ['abcd', 'abce', 'abde', 'acde', 'bcde'], ['abcde']]

count = {}
PI_of_tables = {}

###########     Project     #########

x_lambda = 3
y_lambda = 3
min_area = 1000.0
max_area = 5000.0

grid_x = []
grid_y = []
delta_x, delta_y, delta_area = None, None, None
final_res = []