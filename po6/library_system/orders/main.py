import json
import redis
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()
r = redis.Redis(host="redis", port=6379, decode_responses=True)


# Модель замовлення книги
class Order(BaseModel):
    id: str
    reader_id: str
    book_id: str
    place: str  # 'reading_room' або 'subscription'
    status: str  # 'active' або 'returned'


orders = {}

READERS_SERVICE_URL = "http://readers:8002"
BOOKS_SERVICE_URL = "http://books:8001"


@app.get("/orders", response_model=List[Order])
def get_orders():
    cached_orders = r.get("orders")
    if cached_orders:
        print("Data fetched from cache.")
        return json.loads(cached_orders)

    print("Data fetched from memory.")
    order_list = list(orders.values())
    r.set("orders", json.dumps([order.dict() for order in order_list]), ex=300)  # Оновлюємо кеш списку замовлень
    return order_list


@app.get("/orders/{order_id}")
def get_order(order_id: str):
    cached_order = r.get(f"order:{order_id}")
    if cached_order:
        print(f"Order {order_id} fetched from cache.")
        return json.loads(cached_order)

    print(f"Order {order_id} fetched from memory.")
    if order_id in orders:
        r.set(f"order:{order_id}", json.dumps(orders[order_id].dict()), ex=300)
        return orders[order_id]

    raise HTTPException(status_code=404, detail="Order not found")


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

    # Зменшуємо кількість доступних копій книги (через PUT запит до books_service)
    update_response = requests.put(f"{BOOKS_SERVICE_URL}/books/{order.book_id}/decrease")
    if update_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to update book availability")

    # Замовлення створено
    order.status = "active"
    orders[order.id] = order

    # Оновлюємо кеш для окремого замовлення
    print(f"Order {order.id} created and added to cache.")
    r.set(f"order:{order.id}", json.dumps(order.dict()), ex=300)

    # Оновлюємо кеш списку замовлень
    r.set("orders", json.dumps([order.dict() for order in orders.values()]), ex=300)

    return order


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

    # Оновлюємо кеш для замовлення
    print(f"Order {order_id} status updated to 'returned' and cache refreshed.")
    r.set(f"order:{order_id}", json.dumps(order.dict()), ex=300)

    # Оновлюємо кеш списку замовлень
    r.set("orders", json.dumps([order.dict() for order in orders.values()]), ex=300)

    return {"message": "Book returned successfully"}
