from fastapi import FastAPI
from pydantic import BaseModel
from api.scraping_api import login_and_scrape_rugby_park, login_and_scrape_padel_factory



app = FastAPI()

class ReservationRequest(BaseModel):
    username: str
    password: str
    date: str  # Remplacez "target_date" par "date"
    time: str  # Remplacez "target_time" par "time"


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
    login_url = "https://padelfactory.gestion-sports.com/connexion.php"
    # Remplacez "request.target_date" par "request.date" si nécessaire
    result = await login_and_scrape_padel_factory(
        login_url=login_url,
        username=request.username,
        password=request.password,
        target_date=request.date,
        target_time=request.time
    )
    return result

