# vilcos/routes/websockets.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List
from vilcos.database import get_db
from vilcos import models
from sqlalchemy.orm import Session

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Table status updated: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/reserve")
async def reserve_table(reservation: dict, db: Session = Depends(get_db)):
    # Create reservation logic here
    new_reservation = models.Reservation(**reservation)
    db.add(new_reservation)
    db.commit()
    
    # Broadcast update to all connected clients
    await manager.broadcast("Table status updated")
    
    return {"message": "Reservation created successfully"}

@router.get("/available-tables")
async def get_available_tables(date: str, time_slot_id: int, db: Session = Depends(get_db)):
    # Logic to fetch available tables
    available_tables = db.query(models.Table).filter(
        ~models.Table.reservations.any(
            (models.Reservation.reservation_date == date) &
            (models.Reservation.time_slot_id == time_slot_id)
        )
    ).all()
    
    return {"available_tables": [table.table_number for table in available_tables]}
