import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional


app = FastAPI()

# Модель замовлення книги
class Order(BaseModel):
    id: str  # Залишаємо тип як str
    reader_id: str  # Залишаємо тип як str
    book_id: str  # Залишаємо тип як str
    place: str  # 'reading_room' або 'subscription'
    status: str  # 'active' або 'returned'

orders = {}


READERS_SERVICE_URL = "http://readers:8002"
BOOKS_SERVICE_URL = "http://books:8001"

@app.get("/orders", response_model=List[Order])
def get_orders():
    return list(orders.values())  # Перетворюємо на список для відповіді

@app.post("/orders")
def make_order(order: Order):
    # Перевірка наявності читача через readers_service
    reader_response = requests.get(f"{READERS_SERVICE_URL}/readers/{order.reader_id}")
    if reader_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Reader not found")

    # Перевірка наявності книги та доступності копій через books_service
    book_response = requests.get(f"{BOOKS_SERVICE_URL}/books/search", params={"book_id": order.book_id})
    if book_response.status_code != 200:
        raise HTTPException(status_code=404, detail="Book not found")

    book_data = book_response.json()
    if book_data["available_copies"] <= 0:
        raise HTTPException(status_code=400, detail="No available copies")

    # Зменшуємо кількість доступних копій книги (наприклад, через PUT запит до books_service)
    update_response = requests.put(f"{BOOKS_SERVICE_URL}/books/{order.book_id}/decrease")
    if update_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to update book availability")

    # Замовлення створено
    order.status = "active"
    orders[order.id] = order
    return order

# ---------------------- Повернення книги ------------------------
@app.post("/orders/{order_id}/return")
def return_book(order_id: str):
    if order_id not in orders or orders[order_id].status != 'active':
        raise HTTPException(status_code=404, detail="Active order not found")

    order = orders[order_id]

    # Повертаємо книгу - оновлюємо кількість доступних копій через books_service
    update_response = requests.put(f"{BOOKS_SERVICE_URL}/books/{order.book_id}/increase")
    if update_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to update book availability")

    # Оновлюємо статус замовлення
    order.status = 'returned'
    return {"message": "Book returned successfully"}