from fastapi import FastAPI
from pydantic import BaseModel
from api.scraping_api import main_padel_factory, main_padel_ground



app = FastAPI()

class ReservationRequest(BaseModel):
    username: str
    password: str
    target_date: str
    target_time: str

@app.post("/reserve/padel-ground")
def reserve_padel_ground(request: ReservationRequest):
    result = main_padel_ground(
        request.username,
        request.password,
        request.target_date,
        request.target_time,
    )
    return result

@app.post("/reserve/padel-factory")
async def reserve_padel_factory(request: ReservationRequest):
    terrains = [2519, 2520, 2521, 2522, 755, 756, 757, 758]
    login_url = "https://padelfactory.gestion-sports.com/connexion.php"
    target_url = "https://padelfactory.gestion-sports.com/membre/compte/moyens-paiements.html"
    result = main_padel_factory(
        login_url,
        target_url,
        request.username,
        request.password,
        terrains,
        request.target_date,
        request.target_time,
    )
    return result
