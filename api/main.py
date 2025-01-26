from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from api.scraping_api import main_padel_factory, main_padel_ground
from datetime import datetime, timedelta
import asyncio

app = FastAPI()

class ReservationRequest(BaseModel):
    username: str
    password: str
    target_date: str
    target_time: str

@app.post("/reserve/padel-ground")
async def reserve_padel_ground(request: ReservationRequest):
    max_duration = timedelta(hours=3)  # Durée maximale (3 heures)
    start_time = datetime.now()  # Heure de début des tentatives
    attempt = 1

    while datetime.now() - start_time < max_duration:
        print(f"Tentative {attempt} pour le Padel Ground...")
        result = main_padel_ground(
            request.username,
            request.password,
            request.target_date,
            request.target_time,
        )
        if result:
            return JSONResponse(content={"message": "Réservation réussie."}, status_code=200)
        else:
            print(f"Échec de la tentative {attempt}. Nouvelle tentative dans 30 secondes...")
            attempt += 1
            await asyncio.sleep(30)  # Attendre 30 secondes avant la prochaine tentative

    # Si la durée maximale est atteinte
    return JSONResponse(content={"message": "Échec de la réservation après 3 heures."}, status_code=408)


@app.post("/reserve/padel-factory")
async def reserve_padel_factory(request: ReservationRequest):
    terrains = [2519, 2520, 2521, 2522, 755, 756, 757, 758]
    login_url = "https://padelfactory.gestion-sports.com/connexion.php"
    target_url = "https://padelfactory.gestion-sports.com/membre/compte/moyens-paiements.html"

    # Conversion de la date au format attendu
    print(f"Date de réservation : {request.target_date}")
    date_objet = datetime.strptime(request.target_date, "%Y-%m-%d")
    date = date_objet.strftime("%d/%m/%Y")

    print(f"Heure de réservation : {request.target_time}")

    max_duration = timedelta(hours=3)  # Durée maximale (3 heures)
    start_time = datetime.now()  # Heure de début des tentatives
    attempt = 1

    while datetime.now() - start_time < max_duration:
        print(f"Tentative {attempt} pour le Padel Factory...")
        result = main_padel_factory(
            login_url,
            target_url,
            request.username,
            request.password,
            terrains,
            date,
            request.target_time,
        )
        if result:
            return JSONResponse(content={"message": "Réservation réussie."}, status_code=200)
        else:
            print(f"Échec de la tentative {attempt}. Nouvelle tentative dans 30 secondes...")
            attempt += 1
            await asyncio.sleep(30)  # Attendre 30 secondes avant la prochaine tentative

    # Si la durée maximale est atteinte
    return JSONResponse(content={"message": "Échec de la réservation après 3 heures."}, status_code=408)
