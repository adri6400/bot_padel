from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from api.scraping_api import main_padel_factory, main_padel_ground
from datetime import datetime, timedelta
import asyncio
import json
from pathlib import Path

app = FastAPI()

# Fichier JSON pour enregistrer les recherches
SEARCHES_FILE = Path("searches.json")

# Fonction utilitaire pour charger/enregistrer les recherches
def load_searches():
    if SEARCHES_FILE.exists():
        with open(SEARCHES_FILE, "r") as f:
            return json.load(f)
    return []

def save_searches(data):
    with open(SEARCHES_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Modèles de données
class ReservationRequest(BaseModel):
    username: str
    password: str
    target_date: str
    target_time: str

class StopRequest(BaseModel):
    username: str
    search_id: str

# Flags d'arrêt des recherches
user_stop_flags = {}

@app.post("/stop")
async def stop_reservation(request: StopRequest):
    """
    Arrête une recherche spécifique pour un utilisateur.
    """
    searches = load_searches()
    updated_searches = [
        s for s in searches 
        if s.get("id") != request.search_id or s.get("username") != request.username
    ]

    if len(searches) == len(updated_searches):
        return JSONResponse(
            content={"message": "Aucune recherche correspondante trouvée."},
            status_code=404
        )
    
    save_searches(updated_searches)
    user_stop_flags[request.search_id] = True
    return JSONResponse(content={"message": "Recherche arrêtée avec succès."}, status_code=200)

@app.get("/searches")
async def list_searches():
    """
    Liste toutes les recherches en cours.
    """
    return load_searches()

@app.post("/stop_all")
async def stop_all_searches():
    """
    Arrête toutes les recherches en cours.
    """
    # Charger les recherches
    searches = load_searches()

    # Marquer tous les search_id comme stoppés
    for search in searches:
        search_id = search.get("id")
        user_stop_flags[search_id] = True

    # Vider (ou mettre à jour) la liste des recherches
    save_searches([])

    return JSONResponse(content={"message": "Toutes les recherches ont été arrêtées."}, status_code=200)

@app.post("/reserve/padel-ground")
async def reserve_padel_ground(request: ReservationRequest):
    """
    Recherche pour le Padel Ground.
    """
    search_id = f"{request.username}-{request.target_date}-{request.target_time}-padel-ground"
    
    # Enregistrer la recherche
    searches = load_searches()
    searches.append({
        "id": search_id,
        "username": request.username,
        "date": request.target_date,
        "heure": request.target_time,
        "lieu": "Padel Ground",
        "timestamp": datetime.now().isoformat(),
    })
    save_searches(searches)

    # Initialiser le flag d'arrêt
    user_stop_flags[search_id] = False

    max_duration = timedelta(hours=3)
    start_time = datetime.now()
    attempt = 1

    while datetime.now() - start_time < max_duration:
        if user_stop_flags.get(search_id):
            return JSONResponse(content={"message": "Recherche arrêtée avec succès."}, status_code=200)

        print(f"Tentative {attempt} pour Padel Ground (Utilisateur: {request.username})...")
        # Appel à la fonction spécifique
        result = main_padel_ground(
            request.username,
            request.password,
            request.target_date,
            request.target_time,
        )
        if result:
            user_stop_flags[search_id] = True
            return JSONResponse(content={"message": "Réservation réussie."}, status_code=200)
        
        attempt += 1
        await asyncio.sleep(30)

    return JSONResponse(content={"message": "Durée maximale atteinte sans succès."}, status_code=408)

@app.post("/reserve/padel-factory")
async def reserve_padel_factory(request: ReservationRequest):
    """
    Recherche pour le Padel Factory.
    """
    search_id = f"{request.username}-{request.target_date}-{request.target_time}-padel-factory"

    # Enregistrer la recherche
    searches = load_searches()
    searches.append({
        "id": search_id,
        "username": request.username,
        "date": request.target_date,
        "heure": request.target_time,
        "lieu": "Padel Factory",
        "timestamp": datetime.now().isoformat(),
    })
    save_searches(searches)

    # Initialiser le flag d'arrêt
    user_stop_flags[search_id] = False

    max_duration = timedelta(hours=3)
    start_time = datetime.now()
    attempt = 1

    while datetime.now() - start_time < max_duration:
        if user_stop_flags.get(search_id):
            return JSONResponse(content={"message": "Recherche arrêtée avec succès."}, status_code=200)

        print(f"Tentative {attempt} pour Padel Factory (Utilisateur: {request.username})...")
        # Appel à la fonction spécifique
        result = main_padel_factory(
            "https://padelfactory.gestion-sports.com/connexion.php",
            "https://padelfactory.gestion-sports.com/membre/compte/moyens-paiements.html",
            request.username,
            request.password,
            [2519, 2520, 2521, 2522, 755, 756, 757, 758],
            datetime.strptime(request.target_date, "%Y-%m-%d").strftime("%d/%m/%Y"),
            request.target_time,
        )
        if result:
            user_stop_flags[search_id] = True
            return JSONResponse(content={"message": "Réservation réussie."}, status_code=200)
        
        attempt += 1
        await asyncio.sleep(30)

    return JSONResponse(content={"message": "Durée maximale atteinte sans succès."}, status_code=408)
