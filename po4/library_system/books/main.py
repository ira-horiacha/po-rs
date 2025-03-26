from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Модель книги
class Book(BaseModel):
    id: str  # Залишаємо тип як str
    title: str
    author: str
    total_copies: int   # Загальна кількість копій
    available_copies: int  # Доступні копії для видачі

books = {}

@app.get("/books", response_model=List[Book])
def get_books():
    return list(books.values())  # Перетворюємо на список для відповіді

@app.post("/books")
def add_book(book: Book):
    books[book.id] = book
    return book

@app.get("/books/search")
def get_book(book_id: str):
    for book in books.values():
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.put("/books/{book_id}")
def update_book(book_id: str, updated_book: Book):
    if book_id in books:
        books[book_id] = updated_book
        return updated_book
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}")
def delete_book(book_id: str):
    if book_id in books:
        del books[book_id]
        return {"message": "Book deleted"}
    raise HTTPException(status_code=404, detail="Book not found")

@app.put("/books/{book_id}/decrease")
def decrease_book(book_id: str):
    if book_id in books and books[book_id].available_copies > 0:
        books[book_id].available_copies -= 1
        return {"message": "Book reserved"}
    raise HTTPException(status_code=400, detail="No available copies")

@app.put("/books/{book_id}/increase")
def increase_book(book_id: str):
    if book_id in books:
        books[book_id].available_copies += 1
        return {"message": "Book returned"}
    raise HTTPException(status_code=404, detail="Book not found")