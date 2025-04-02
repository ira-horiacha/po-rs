import json
import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()
r = redis.Redis(host="redis", port=6379, decode_responses=True)  # Підключення до Redis

# Модель книги
class Book(BaseModel):
    id: str
    title: str
    author: str
    total_copies: int
    available_copies: int

books = {}

@app.get("/books", response_model=List[Book])
def get_books():
    cached_books = r.get("books")
    if cached_books:
        print("Data fetched from cache.")  # Вивід у консоль
        return json.loads(cached_books)

    print("Data fetched from memory.")  # Вивід у консоль
    book_list = list(books.values())
    # Перетворення об'єктів на словники перед серіалізацією
    r.set("books", json.dumps([book.dict() for book in book_list]), ex=300)  # Термін дії кешу - 5 хвилин
    return book_list

@app.post("/books")
def add_book(book: Book):
    books[book.id] = book
    r.delete("books")  # Очищаємо кеш списку книг
    print("Book added to memory and cache cleared.")  # Вивід у консоль
    return book

@app.get("/books/search")
def get_book(book_id: str):
    cached_book = r.get(f"book:{book_id}")
    if cached_book:
        print(f"Data for book {book_id} fetched from cache.")  # Вивід у консоль
        return json.loads(cached_book)

    print(f"Data for book {book_id} fetched from memory.")  # Вивід у консоль
    if book_id in books:
        r.set(f"book:{book_id}", json.dumps(books[book_id].dict()), ex=300)
        return books[book_id]
    raise HTTPException(status_code=404, detail="Book not found")

@app.put("/books/{book_id}")
def update_book(book_id: str, updated_book: Book):
    if book_id in books:
        books[book_id] = updated_book
        r.set(f"book:{book_id}", json.dumps(updated_book.dict()), ex=300)  # Оновлюємо кеш книги
        r.delete("books")  # Очищаємо кеш списку книг
        print(f"Book {book_id} updated in memory and cache.")  # Вивід у консоль
        return updated_book
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}")
def delete_book(book_id: str):
    if book_id in books:
        del books[book_id]
        r.delete(f"book:{book_id}")  # Видаляємо кеш книги
        r.delete("books")  # Очищаємо кеш списку книг
        print(f"Book {book_id} deleted from memory and cache.")  # Вивід у консоль
        return {"message": f"Book {book_id} deleted."}
    raise HTTPException(status_code=404, detail="Book not found")

# Доданий ендпоінт для зменшення кількості доступних копій
@app.put("/books/{book_id}/decrease")
def decrease_book_copies(book_id: str):
    if book_id in books:
        book = books[book_id]
        if book.available_copies > 0:
            book.available_copies -= 1
            r.set(f"book:{book_id}", json.dumps(book.dict()), ex=300)  # Оновлюємо кеш книги
            r.delete("books")  # Очищаємо кеш списку книг
            print(f"Decreased available copies for book {book_id}. New available copies: {book.available_copies}")
            return {"message": f"Available copies for book {book_id} decreased successfully"}
        else:
            raise HTTPException(status_code=400, detail="No available copies to decrease")
    raise HTTPException(status_code=404, detail="Book not found")

# Доданий ендпоінт для збільшення кількості доступних копій (повернення книги)
@app.put("/books/{book_id}/increase")
def increase_book_copies(book_id: str):
    if book_id in books:
        book = books[book_id]
        if book.available_copies < book.total_copies:
            book.available_copies += 1
            r.set(f"book:{book_id}", json.dumps(book.dict()), ex=300)  # Оновлюємо кеш книги
            r.delete("books")  # Очищаємо кеш списку книг
            print(f"Increased available copies for book {book_id}. New available copies: {book.available_copies}")
            return {"message": f"Available copies for book {book_id} increased successfully"}
        else:
            raise HTTPException(status_code=400, detail="All copies are already available")
    raise HTTPException(status_code=404, detail="Book not found")
