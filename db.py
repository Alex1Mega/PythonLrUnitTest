import sqlalchemy as db
from sqlalchemy.orm import DeclarativeBase, sessionmaker
# print(sqlalchemy.__version__)

DATABASE_URL = "sqlite:///./time_interval.db"
engine = db.create_engine(DATABASE_URL)
# conn = engine.connect()

metadata = db.MetaData()
time_interval = db.Table(
    'time_interval',
    metadata,
    db.Column('Id', db.Integer, primary_key=True),
    db.Column('Total_seconds', db.Integer, nullable=False))

metadata.create_all(engine)