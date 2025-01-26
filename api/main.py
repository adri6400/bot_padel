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

# Dictionnaire pour suivre les flags d'arrêt pour chaque utilisateur
user_stop_flags = {}

@app.post("/stop")
async def stop_reservation(username: str):
    """
    Arrête les tentatives de réservation pour un utilisateur spécifique.
    Args:
        username (str): Identifiant de l'utilisateur.
    """
    if username not in user_stop_flags:
        return JSONResponse(content={"message": f"Aucune recherche active trouvée pour l'utilisateur '{username}'."}, status_code=404)
    user_stop_flags[username] = True
    return JSONResponse(content={"message": f"Arrêt des tentatives pour l'utilisateur '{username}'."}, status_code=200)

@app.post("/reserve/padel-ground")
async def reserve_padel_ground(request: ReservationRequest):
    # Initialiser le flag d'arrêt pour cet utilisateur
    user_stop_flags[request.username] = False

    max_duration = timedelta(hours=3)  # Durée maximale (3 heures)
    start_time = datetime.now()  # Heure de début des tentatives
    attempt = 1

    while datetime.now() - start_time < max_duration:
        if user_stop_flags.get(request.username):
            return JSONResponse(content={"message": f"Recherche arrêtée pour l'utilisateur '{request.username}'."}, status_code=200)

        print(f"Tentative {attempt} pour le Padel Ground (Utilisateur: {request.username})...")
        result = main_padel_ground(
            request.username,
            request.password,
            request.target_date,
            request.target_time,
        )
        if result:
            # Stopper uniquement les recherches pour cet utilisateur
            user_stop_flags[request.username] = True
            return JSONResponse(content={"message": f"Réservation réussie au Padel Ground pour '{request.username}'."}, status_code=200)
        else:
            print(f"Échec de la tentative {attempt} pour '{request.username}'. Nouvelle tentative dans 30 secondes...")
            attempt += 1
            await asyncio.sleep(30)  # Attendre 30 secondes avant la prochaine tentative

    # Si la durée maximale est atteinte
    return JSONResponse(content={"message": f"Échec de la réservation après 3 heures pour '{request.username}'."}, status_code=408)


@app.post("/reserve/padel-factory")
async def reserve_padel_factory(request: ReservationRequest):
    # Initialiser le flag d'arrêt pour cet utilisateur
    user_stop_flags[request.username] = False

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
        if user_stop_flags.get(request.username):
            return JSONResponse(content={"message": f"Recherche arrêtée pour l'utilisateur '{request.username}'."}, status_code=200)

        print(f"Tentative {attempt} pour le Padel Factory (Utilisateur: {request.username})...")
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
            # Stopper uniquement les recherches pour cet utilisateur
            user_stop_flags[request.username] = True
            return JSONResponse(content={"message": f"Réservation réussie au Padel Factory pour '{request.username}'."}, status_code=200)
        else:
            print(f"Échec de la tentative {attempt} pour '{request.username}'. Nouvelle tentative dans 30 secondes...")
            attempt += 1
            await asyncio.sleep(30)  # Attendre 30 secondes avant la prochaine tentative

    # Si la durée maximale est atteinte
    return JSONResponse(content={"message": f"Échec de la réservation après 3 heures pour '{request.username}'."}, status_code=408)
