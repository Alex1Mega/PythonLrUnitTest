import fastapi as api
from db import engine, time_interval
import sqlalchemy as sqla
from pydantic import BaseModel
from main import TimeInterval

app = api.FastAPI()

def get_engine():
    return engine

class IntReq(BaseModel):
    Total_seconds: int

class IntRes(BaseModel):
    Id: int
    Total_seconds: int

# @app.get("/")
# async def root():
#     return {"Hello": "World"}
#
# @app.post("/time")
# def create_time(total_seconds: int):
#     with engine.connect() as db:
#         result = db.execute(time_interval.insert().values(Total_seconds=total_seconds))
#         db.commit()
#
#     return {
#         "id": result.inserted_primary_key[0],
#         "total_seconds": total_seconds
#     }
#
# @app.get("/time")
# def get_times():
#     with engine.connect() as db:
#         result = db.execute(time_interval.select())
#         return [dict(row._mapping) for row in result]

@app.post("/intervals", response_model=IntRes, status_code=201)
def create_interval(data: IntReq, db_engine=api.Depends(get_engine)):
    check = TimeInterval(total_seconds=data.total_seconds)
    with db_engine.connect() as connection:
        result = connection.execute(time_interval.insert().values(Total_seconds=data.total_seconds))
        connection.commit()
        return {
            "id": result.inserted_primary_key[0],
            "total_seconds": data.total_seconds
        }


@app.get("/intervals/{id}", response_model=IntRes, status_code=200)
def get_interval(id: int, db_engine=api.Depends(get_engine)):
    with db_engine.connect() as connection:
        result = connection.execute(sqla.select(time_interval).where(time_interval.c.Id == id)).first()
        return dict(result._mapping)


@app.get("/intervals", response_model=list[IntRes], status_code=200)
def get_intervals(db_engine=api.Depends(get_engine)):
    with db_engine.connect() as connection:
        result = connection.execute(sqla.select(time_interval))
        return [dict(row._mapping) for row in result]


@app.delete("/intervals/{id}", status_code=200)
def delete_interval(id: int, db_engine=api.Depends(get_engine)):
    with db_engine.connect() as connection:
        result = connection.execute(time_interval.delete().where(time_interval.c.Id == id))
        connection.commit()
        return {"message": "Interval deleted"}
