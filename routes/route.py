from fastapi import APIRouter, HTTPException
from api.dtos import HistoryName, HistoryId, HistoryBetween
from database.repositories import HistoryRepository

router = APIRouter(prefix="/history", tags=["History"])

hist_db = HistoryRepository()

@router.post("/get/name/")
async def history_by_name(history: HistoryName):
    try:
        result = hist_db.get_by_product_name(history.product_name, history.days)
    except Exception as e: 
        print(f"Requisição com erro de: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    if result is None:
        return { }
    
    return result 
