import requests

def call_padel_factory_api():
    # Définir l'URL de l'API
    api_url = "https://bot-padel.onrender.com/reserve/padel-factory"

    # Données à envoyer à l'API
    data = {
        "login_url": "https://padelfactory.gestion-sports.com/connexion.php",
        "username": "bernardadrien26@gmail.com",
        "password": "Espasers64_",
        "target_date": "2025-01-17",  # Remplacez par votre date cible
        "target_time": "09:00"  # Remplacez par votre horaire cible
    }

    try:
        # Effectuer une requête POST
        response = requests.post(api_url, json=data)

        # Vérifier si la requête a réussi
        if response.status_code == 200:
            print("Réponse de l'API :", response.json())
        else:
            print(f"Erreur {response.status_code}: {response.text}")
    except Exception as e:
        print("Erreur lors de l'appel à l'API :", e)

# Appeler la fonction
call_padel_factory_api()