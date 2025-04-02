import json
import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()
r = redis.Redis(host="redis", port=6379, decode_responses=True)


# Модель читача
class Reader(BaseModel):
    id: str
    name: str


readers = {}


@app.get("/readers", response_model=List[Reader])
def get_readers():
    cached_readers = r.get("readers")
    if cached_readers:
        print("Data fetched from cache for readers.")
        return json.loads(cached_readers)

    print("Data fetched from memory for readers.")
    reader_list = list(readers.values())
    # Перетворюємо список читачів на словники
    r.set("readers", json.dumps([reader.dict() for reader in reader_list]), ex=300)  # Кешуємо список читачів
    return reader_list


@app.post("/readers")
def add_reader(reader: Reader):
    readers[reader.id] = reader

    # Оновлюємо кеш для нового читача
    print(f"Reader {reader.id} added. Adding to reader cache.")
    r.set(f"reader:{reader.id}", json.dumps(reader.dict()), ex=300)

    # Оновлюємо кеш списку читачів
    r.set("readers", json.dumps([r.dict() for r in readers.values()]), ex=300)

    return reader


@app.get("/readers/{reader_id}")
def get_reader(reader_id: str):
    cached_reader = r.get(f"reader:{reader_id}")
    if cached_reader:
        print(f"Reader {reader_id} fetched from cache.")
        return json.loads(cached_reader)

    print(f"Reader {reader_id} fetched from memory.")
    if reader_id in readers:
        r.set(f"reader:{reader_id}", json.dumps(readers[reader_id].dict()), ex=300)
        return readers[reader_id]

    raise HTTPException(status_code=404, detail="Reader not found")


@app.put("/readers/{reader_id}")
def update_reader(reader_id: str, updated_reader: Reader):
    if reader_id in readers:
        readers[reader_id] = updated_reader

        # Оновлюємо кеш для читача
        print(f"Reader {reader_id} updated. Cache refreshed.")
        r.set(f"reader:{reader_id}", json.dumps(updated_reader.dict()), ex=300)

        # Оновлюємо кеш списку читачів
        r.set("readers", json.dumps([r.dict() for r in readers.values()]), ex=300)

        return updated_reader

    raise HTTPException(status_code=404, detail="Reader not found")


@app.delete("/readers/{reader_id}")
def delete_reader(reader_id: str):
    if reader_id in readers:
        del readers[reader_id]

        # Видаляємо читача з кешу
        print(f"Reader {reader_id} deleted. Cache refreshed.")
        r.delete(f"reader:{reader_id}")

        # Оновлюємо кеш списку читачів
        r.set("readers", json.dumps([r.dict() for r in readers.values()]), ex=300)

        return {"message": "Reader deleted successfully"}

    raise HTTPException(status_code=404, detail="Reader not found")
