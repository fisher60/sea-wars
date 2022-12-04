from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import DATABASE_URL

# check_same_thread for sqlite only
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

sql_base = declarative_base()
