import fastapi as api
from db import engine, time_interval

app = api.FastAPI()

@app.get("/")
async def root():
    return {"Hello": "World"}

@app.post("/time")
def create_time(total_seconds: int):
    with engine.connect() as db:
        result = db.execute(time_interval.insert().values(Total_seconds=total_seconds))
        db.commit()

    return {
        "id": result.inserted_primary_key[0],
        "total_seconds": total_seconds
    }

@app.get("/time")
def get_times():
    with engine.connect() as db:
        result = db.execute(time_interval.select())
        return [dict(row._mapping) for row in result]
