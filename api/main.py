from fastapi import FastAPI, Header, HTTPException, Path, Query
from pydantic import BaseModel
from typing import List
import os

app = FastAPI(
    title="Example REST API",
    description="Et eksempel på et standard REST API med FastAPI",
    version="1.0.0"
)

# --- API-key ---
API_KEY = os.environ.get("API_KEY", "defaultkey")

def verify_api_key(api_key: str):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# --- Data model ---
class Item(BaseModel):
    id: int
    name: str
    description: str | None = None

# --- Simuleret database ---
db: List[Item] = [
    Item(id=1, name="Item 1", description="First item"),
    Item(id=2, name="Item 2", description="Second item")
]

# --- Endpoints ---
@app.get("/status")
def status():
    return {"status": "ok"}

@app.get("/items")
def get_items(api_key: str = Header(None)):
    verify_api_key(api_key)
    return db

@app.get("/items/{item_id}")
def get_item(item_id: int = Path(..., gt=0), api_key: str = Header(None)):
    verify_api_key(api_key)
    for item in db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/search")
def search_items(name: str = Query(..., min_length=1), api_key: str = Header(None)):
    verify_api_key(api_key)
    results = [item for item in db if name.lower() in item.name.lower()]
    return {"results": results}

@app.post("/items")
def create_item(item: Item, api_key: str = Header(None)):
    verify_api_key(api_key)
    db.append(item)
    return {"message": "Item created", "item": item}

@app.put("/items/{item_id}")
def update_item(
    item_id: int = Path(..., gt=0),
    updated_item: Item = None,
    api_key: str = Header(None)
):
    verify_api_key(api_key)
    
    for i, item in enumerate(db):
        if item.id == item_id:
            db[i] = updated_item
            return {"message": "Item updated", "item": updated_item}
    
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{item_id}")
def delete_item(item_id: int, api_key: str = Header(None)):
    verify_api_key(api_key)
    for i, item in enumerate(db):
        if item.id == item_id:
            deleted_item = db.pop(i)
            return {"message": "Item deleted", "item": deleted_item}
    raise HTTPException(status_code=404, detail="Item not found")
