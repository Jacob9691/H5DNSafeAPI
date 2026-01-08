from fastapi import FastAPI, Header, HTTPException, Path, Query, Request
from pydantic import BaseModel
from typing import List
import os
import logging

# --- Logging setup ---
logging.basicConfig(
    filename="/var/log/api.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Example REST API",
    description="Et eksempel på et standard REST API med FastAPI",
    version="1.0.0"
)

# --- API-key ---
API_KEY = os.environ.get("API_KEY", "defaultkey")

def verify_api_key(api_key: str, request: Request):
    if api_key != API_KEY:
        logger.warning(
            "Unauthorized access attempt from %s",
            request.client.host
        )
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
    logger.info("Status check called")
    return {"status": "ok"}

@app.get("/items")
def get_items(request: Request, api_key: str = Header(None)):
    verify_api_key(api_key, request)
    logger.info("Fetched all items from %s", request.client.host)
    return db

@app.get("/items/{item_id}")
def get_item(
    request: Request,
    item_id: int = Path(..., gt=0),
    api_key: str = Header(None)
):
    verify_api_key(api_key, request)
    for item in db:
        if item.id == item_id:
            logger.info(
                "Item %s fetched from %s",
                item_id,
                request.client.host
            )
            return item

    logger.warning("Item %s not found", item_id)
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/search")
def search_items(
    request: Request,
    name: str = Query(..., min_length=1),
    api_key: str = Header(None)
):
    verify_api_key(api_key, request)
    results = [item for item in db if name.lower() in item.name.lower()]
    logger.info(
        "Search for '%s' from %s returned %d results",
        name,
        request.client.host,
        len(results)
    )
    return {"results": results}

@app.post("/items")
def create_item(
    request: Request,
    item: Item,
    api_key: str = Header(None)
):
    verify_api_key(api_key, request)
    db.append(item)
    logger.info(
        "Item %s created from %s",
        item.id,
        request.client.host
    )
    return {"message": "Item created", "item": item}

@app.put("/items/{item_id}")
def update_item(
    request: Request,
    item_id: int = Path(..., gt=0),
    updated_item: Item = None,
    api_key: str = Header(None)
):
    verify_api_key(api_key, request)

    for i, item in enumerate(db):
        if item.id == item_id:
            db[i] = updated_item
            logger.info(
                "Item %s updated from %s",
                item_id,
                request.client.host
            )
            return {"message": "Item updated", "item": updated_item}

    logger.warning("Update failed item %s not found", item_id)
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{item_id}")
def delete_item(
    request: Request,
    item_id: int,
    api_key: str = Header(None)
):
    verify_api_key(api_key, request)
    for i, item in enumerate(db):
        if item.id == item_id:
            deleted_item = db.pop(i)
            logger.info(
                "Item %s deleted from %s",
                item_id,
                request.client.host
            )
            return {"message": "Item deleted", "item": deleted_item}

    logger.warning("Delete failed item %s not found", item_id)
    raise HTTPException(status_code=404, detail="Item not found")
