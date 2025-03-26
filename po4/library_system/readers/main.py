from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()


# Модель читача
class Reader(BaseModel):
    id: str  # Залишаємо тип як str
    name: str

readers = {}

@app.get("/readers", response_model=List[Reader])
def get_readers():
    return list(readers.values())  # Перетворюємо на список для відповіді

@app.post("/readers")
def add_reader(reader: Reader):
    readers[reader.id] = reader
    return reader

@app.get("/readers/{reader_id}")
def get_reader(reader_id: str):
    if reader_id in readers:
        return readers[reader_id]
    raise HTTPException(status_code=404, detail="Reader not found")

@app.put("/readers/{reader_id}")
def update_reader(reader_id: str, updated_reader: Reader):
    if reader_id in readers:
        readers[reader_id] = updated_reader
        return updated_reader
    raise HTTPException(status_code=404, detail="Reader not found")

@app.delete("/readers/{reader_id}")
def delete_reader(reader_id: str):
    if reader_id in readers:
        del readers[reader_id]
        return {"message": "Reader deleted"}
    raise HTTPException(status_code=404, detail="Reader not found")