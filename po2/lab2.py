from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()


# Модель рейсу
class Flight(BaseModel):
    id: int
    number: str
    from_point: str
    to_point: str
    departure_time: str
    arrival_time: str
    status: str


flights = []  # Збереження рейсів у пам'яті


# Модель літака
class Aircraft(BaseModel):
    id: int
    model: str
    capacity: int
    airline: str


aircrafts = []  # Збереження літаків у пам'яті


# Модель пасажира
class Passenger(BaseModel):
    id: int
    name: str
    passport_number: str
    flight_id: int  # ID рейсу, до якого прив'язаний пасажир


passengers = []  # Збереження пасажирів у пам'яті


# ------------------ CRUD для рейсів ------------------

@app.get("/flights", response_model=List[Flight])
def get_flights():
    return flights


@app.post("/flights")
def add_flight(flight: Flight):
    flights.append(flight)
    return flight


@app.get("/flights/{flight_id}")
def get_flight(flight_id: int):
    for flight in flights:
        if flight.id == flight_id:
            return flight
    raise HTTPException(status_code=404, detail="Flight not found")


@app.put("/flights/{flight_id}")
def update_flight(flight_id: int, updated_flight: Flight):
    for i, flight in enumerate(flights):
        if flight.id == flight_id:
            flights[i] = updated_flight
            return updated_flight
    raise HTTPException(status_code=404, detail="Flight not found")


@app.delete("/flights/{flight_id}")
def delete_flight(flight_id: int):
    for i, flight in enumerate(flights):
        if flight.id == flight_id:
            del flights[i]
            return {"message": "Flight deleted"}
    raise HTTPException(status_code=404, detail="Flight not found")


# ------------------ CRUD для літаків ------------------

@app.get("/aircrafts", response_model=List[Aircraft])
def get_aircrafts():
    return aircrafts


@app.post("/aircrafts")
def add_aircraft(aircraft: Aircraft):
    aircrafts.append(aircraft)
    return aircraft


@app.get("/aircrafts/{aircraft_id}")
def get_aircraft(aircraft_id: int):
    for aircraft in aircrafts:
        if aircraft.id == aircraft_id:
            return aircraft
    raise HTTPException(status_code=404, detail="Aircraft not found")


@app.put("/aircrafts/{aircraft_id}")
def update_aircraft(aircraft_id: int, updated_aircraft: Aircraft):
    for i, aircraft in enumerate(aircrafts):
        if aircraft.id == aircraft_id:
            aircrafts[i] = updated_aircraft
            return updated_aircraft
    raise HTTPException(status_code=404, detail="Aircraft not found")


@app.delete("/aircrafts/{aircraft_id}")
def delete_aircraft(aircraft_id: int):
    for i, aircraft in enumerate(aircrafts):
        if aircraft.id == aircraft_id:
            del aircrafts[i]
            return {"message": "Aircraft deleted"}
    raise HTTPException(status_code=404, detail="Aircraft not found")


# ------------------ CRUD для пасажирів ------------------

@app.get("/passengers", response_model=List[Passenger])
def get_passengers():
    return passengers


@app.post("/passengers")
def add_passenger(passenger: Passenger):
    # Переконуємось, що рейс існує перед додаванням пасажира
    if not any(flight.id == passenger.flight_id for flight in flights):
        raise HTTPException(status_code=400, detail="Flight not found")

    passengers.append(passenger)
    return passenger


@app.get("/passengers/{passenger_id}")
def get_passenger(passenger_id: int):
    for passenger in passengers:
        if passenger.id == passenger_id:
            return passenger
    raise HTTPException(status_code=404, detail="Passenger not found")


@app.put("/passengers/{passenger_id}")
def update_passenger(passenger_id: int, updated_passenger: Passenger):
    for i, passenger in enumerate(passengers):
        if passenger.id == passenger_id:
            passengers[i] = updated_passenger
            return updated_passenger
    raise HTTPException(status_code=404, detail="Passenger not found")


@app.delete("/passengers/{passenger_id}")
def delete_passenger(passenger_id: int):
    for i, passenger in enumerate(passengers):
        if passenger.id == passenger_id:
            del passengers[i]
            return {"message": "Passenger deleted"}
    raise HTTPException(status_code=404, detail="Passenger not found")
