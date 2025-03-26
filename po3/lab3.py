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

# Модель читача
class Reader(BaseModel):
    id: str  # Залишаємо тип як str
    name: str

readers = {}

# Модель замовлення книги
class Order(BaseModel):
    id: str  # Залишаємо тип як str
    reader_id: str  # Залишаємо тип як str
    book_id: str  # Залишаємо тип як str
    place: str  # 'reading_room' або 'subscription'
    status: str  # 'active' або 'returned'

orders = {}

# ----------------------й для книг ------------------------

@app.get("/books", response_model=List[Book])
def get_books():
    return list(books.values())  # Перетворюємо на список для відповіді

@app.post("/books")
def add_book(book: Book):
    books[book.id] = book
    return book

@app.get("/books/search")
def get_book(book_id: Optional[str] = None, book_title: Optional[str] = None):
    for book in books.values():
        if (book_id is not None and book.id == book_id) and \
           (book_title is not None and book.title.lower() == book_title.lower()):
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

# ---------------------- CRUD для читачів ------------------------

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

# ---------------------- Замовлення книги ------------------------

@app.get("/orders", response_model=List[Order])
def get_orders():
    return list(orders.values())  # Перетворюємо на список для відповіді

@app.post("/orders")
def make_order(order: Order):
    # Перевірка наявності читача
    if order.reader_id not in readers:
        raise HTTPException(status_code=400, detail="Reader not found")

    # Перевірка чи є книга та доступна до видачі
    if order.book_id in books:
        book = books[order.book_id]
        if book.available_copies > 0:
            book.available_copies -= 1  # Блокуємо 1 копію
            order.status = 'active'
            orders[order.id] = order
            return order
        else:
            raise HTTPException(status_code=400, detail="No available copies")
    raise HTTPException(status_code=404, detail="Book not found")

# ---------------------- Повернення книги ------------------------

@app.post("/orders/{order_id}/return")
def return_book(order_id: str):
    if order_id in orders and orders[order_id].status == 'active':
        order = orders[order_id]
        book = books.get(order.book_id)
        if book:
            book.available_copies += 1
            order.status = 'returned'
            return {"message": "Book returned successfully"}
        raise HTTPException(status_code=404, detail="Book not found during return")
    raise HTTPException(status_code=404, detail="Active order not found")
