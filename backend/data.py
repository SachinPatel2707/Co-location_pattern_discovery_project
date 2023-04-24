from backend.db_connection import connect_to_db
from sqlalchemy import text

dist_h = 12000
PI = 0.3
gurugram_long = 77.026344
gurugram_lat = 28.457523
meerut_long = 77.705956
meerut_lat = 28.984644

db_conn = connect_to_db()

tables = [[], ['a', 'b', 'c', 'd', 'e']]
# tables = [[], ['a', 'b', 'c']]

delete_tables = [['a', 'b', 'c', 'd', 'e'], ['ab', 'ac', 'ad', 'ae', 'bc', 'bd', 'be', 'cd', 'ce', 'de'], ['abc', 'abd', 'abe', 'acd', 'ace', 'ade', 'bcd', 'bce', 'bde', 'cde'], ['abcd', 'abce', 'abde', 'acde', 'bcde'], ['abcde']]

count = {}
PI_of_tables = {}