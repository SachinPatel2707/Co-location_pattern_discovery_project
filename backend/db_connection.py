from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def connect_to_db():
    engine = create_engine('postgresql://sam:hunterr@127.0.0.1:5432/assignment1', isolation_level="AUTOCOMMIT")
    conn = engine.connect()
    return conn