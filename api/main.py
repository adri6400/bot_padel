from fastapi import FastAPI
from pydantic import BaseModel
from api.scraping_api import login_and_scrape_rugby_park, login_and_scrape_padel_factory



app = FastAPI()

class ReservationRequest(BaseModel):
    login_url: str
    username: str
    password: str
    target_date: str
    target_time: str

@app.post("/reserve/rugby-park")
async def reserve_rugby_park(request: ReservationRequest):
    result = await login_and_scrape_rugby_park(
        request.login_url,
        request.username,
        request.password,
        request.target_date,
        request.target_time,
    )
    return result

@app.post("/reserve/padel-factory")
async def reserve_padel_factory(request: ReservationRequest):
    # result = await login_and_scrape_padel_factory(
    #     request.login_url,
    #     request.username,
    #     request.password,
    #     request.target_date,
    #     request.target_time,
    # )
    
    #return result
    return {"success": True, "message": f"Réservation à {request.date} à {request.time}"}
